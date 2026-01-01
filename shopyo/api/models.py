"""
Enhanced DB-related helper utilities for Flask applications.
Provides powerful mixins and base classes for rapid development.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from sqlalchemy import Column, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query

sys.path.append(os.getcwd())
from init import db

T = TypeVar("T", bound="YoModel")

# Use timezone.utc for compatibility with Python < 3.11
UTC = timezone.utc


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""

    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin that adds soft delete functionality."""

    is_deleted = Column(Boolean, default=False, nullable=False)

    def soft_delete(self, commit: bool = True) -> Optional["SoftDeleteMixin"]:
        """Soft delete the record by setting is_deleted to True."""
        self.is_deleted = True
        if commit:
            self.save()
            return self
        return None

    @classmethod
    def get_active(cls) -> Query:
        """Get all non-deleted records."""
        return cls.query.filter_by(is_deleted=False)


class ValidationMixin:
    """Mixin that adds validation functionality."""

    def validate(self) -> List[str]:
        """Validate the model instance.

        Returns:
            List[str]: List of validation errors, empty if valid
        """
        return []

    def is_valid(self) -> bool:
        """Check if the model instance is valid."""
        return len(self.validate()) == 0


class SearchMixin:
    """Mixin that adds search functionality."""

    @classmethod
    def search(cls, query: str, fields: List[str]) -> Query:
        """Search records by query string in specified fields.

        Args:
            query (str): Search query
            fields (List[str]): List of field names to search in

        Returns:
            Query: SQLAlchemy query with search filters
        """
        search_conditions = []
        for field in fields:
            if hasattr(cls, field):
                search_conditions.append(getattr(cls, field).ilike(f"%{query}%"))
        return cls.query.filter(db.or_(*search_conditions))


class PaginationMixin:
    """Mixin that adds pagination functionality."""

    @classmethod
    def paginate(cls, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Paginate records.

        Args:
            page (int): Page number
            per_page (int): Number of items per page

        Returns:
            Dict[str, Any]: Dictionary containing paginated items and metadata
        """
        pagination = cls.query.paginate(page=page, per_page=per_page)
        return {
            "items": pagination.items,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }


class CRUDMixin:
    """
    Mixin that adds convenience methods for
    CRUD (create, read, update, delete) operations.
    """

    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        """Create a new record and save it in the database.

        Returns:
            T: The created record
        """
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit: bool = True, **kwargs) -> Optional[T]:
        """Update specific fields of a record.

        Args:
            commit (bool): Whether to commit the changes
            **kwargs: Fields to update

        Returns:
            Optional[T]: The updated record if committed, None otherwise
        """
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        if commit:
            self.save()
            return self
        return None

    def save(self, commit: bool = True) -> T:
        """Save the record.

        Args:
            commit (bool): Whether to commit the changes

        Returns:
            T: The saved record
        """
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit: bool = True) -> Optional[T]:
        """Remove the record from the database.

        Args:
            commit (bool): Whether to commit the changes

        Returns:
            Optional[T]: The deleted record if committed, None otherwise
        """
        db.session.delete(self)
        if commit:
            db.session.commit()
            return self
        return None

    @classmethod
    def bulk_create(cls: Type[T], items: List[Dict[str, Any]]) -> List[T]:
        """Create multiple records at once.

        Args:
            items (List[Dict[str, Any]]): List of dictionaries containing record data

        Returns:
            List[T]: List of created records
        """
        instances = [cls(**item) for item in items]
        db.session.bulk_save_objects(instances)
        db.session.commit()
        return instances


class YoModel(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically."""
        return cls.__name__.lower()


class PkModel(YoModel):
    """
    Base model class that includes CRUD convenience methods,
    plus adds a 'primary key' column named 'id'.
    """

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls: Type[T], record_id: Union[int, str]) -> Optional[T]:
        """Get record by ID.

        Args:
            record_id (Union[int, str]): ID of record to get

        Returns:
            Optional[T]: Object identified by record_id if any, None otherwise
        """
        if any(
            (
                isinstance(record_id, (str, bytes)) and record_id.isdigit(),
                isinstance(record_id, (int, float)),
            )
        ):
            return cls.query.get(int(record_id))
        return None

    @classmethod
    def get_or_404(cls: Type[T], record_id: Union[int, str]) -> T:
        """Get record by ID or raise 404 error.

        Args:
            record_id (Union[int, str]): ID of record to get

        Returns:
            T: Object identified by record_id

        Raises:
            werkzeug.exceptions.NotFound: If record not found
        """
        from flask import abort

        rv = cls.get_by_id(record_id)
        if rv is None:
            abort(404)
        return rv
