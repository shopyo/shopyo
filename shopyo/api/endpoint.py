"""
endpoint.py

A powerful utility for building RESTful API endpoints in Flask applications.
Provides decorators and base classes for rapid API development with common patterns.
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from flask import request, current_app
from sqlalchemy.orm import Query

from .models import YoModel
from .response import json_response, error_response, paginated_response

T = TypeVar("T", bound=YoModel)


class APIEndpoint:
    """
    A utility class for building RESTful API endpoints with common patterns.
    Provides decorators and methods for handling CRUD operations, validation,
    and response formatting.
    """

    def __init__(self, model_class: Type[T]):
        """
        Initialize the API endpoint with a model class.

        Args:
            model_class (Type[T]): The SQLAlchemy model class to use
        """
        self.model_class = model_class

    def validate_request(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate request data. Override this method in subclasses.

        Args:
            data (Dict[str, Any]): Request data to validate

        Returns:
            List[str]: List of validation errors, empty if valid
        """
        return []

    def format_response(self, data: Any) -> Dict[str, Any]:
        """
        Format response data. Override this method in subclasses.

        Args:
            data (Any): Data to format

        Returns:
            Dict[str, Any]: Formatted response data
        """
        return data

    def get_query_filters(self) -> Dict[str, Any]:
        """
        Get query filters from request args. Override this method in subclasses.

        Returns:
            Dict[str, Any]: Query filters
        """
        return {}

    def handle_list(self, page: int = 1, per_page: int = 20) -> tuple:
        """
        Handle GET request for listing items with pagination.

        Args:
            page (int): Page number
            per_page (int): Items per page

        Returns:
            tuple: Flask response tuple
        """
        try:
            filters = self.get_query_filters()
            query = self.model_class.query.filter_by(**filters)

            # Handle search if search parameter is present
            if "search" in request.args:
                search_query = request.args.get("search", "")
                if hasattr(self.model_class, "search"):
                    query = self.model_class.search(
                        search_query, ["name", "description"]
                    )

            # Handle sorting
            if "sort_by" in request.args:
                sort_by = request.args.get("sort_by")
                if hasattr(self.model_class, sort_by):
                    sort_field = getattr(self.model_class, sort_by)
                    order = request.args.get("order", "asc")
                    if order == "desc":
                        query = query.order_by(sort_field.desc())
                    else:
                        query = query.order_by(sort_field.asc())

            pagination = query.paginate(page=page, per_page=per_page)
            items = [self.format_response(item) for item in pagination.items]

            return paginated_response(
                items=items, total=pagination.total, page=page, per_page=per_page
            )
        except Exception as e:
            current_app.logger.error(f"Error in list endpoint: {str(e)}")
            return error_response("Failed to fetch items", status=500)

    def handle_create(self) -> tuple:
        """
        Handle POST request for creating a new item.

        Returns:
            tuple: Flask response tuple
        """
        try:
            data = request.get_json()
            if not data:
                return error_response("No data provided", status=400)

            # Validate request data
            errors = self.validate_request(data)
            if errors:
                return error_response("Validation failed", errors=errors, status=400)

            # Create new instance
            instance = self.model_class.create(**data)
            return json_response(
                data=self.format_response(instance),
                message="Item created successfully",
                status=201,
            )
        except Exception as e:
            current_app.logger.error(f"Error in create endpoint: {str(e)}")
            return error_response("Failed to create item", status=500)

    def handle_get(self, item_id: Union[int, str]) -> tuple:
        """
        Handle GET request for retrieving a single item.

        Args:
            item_id (Union[int, str]): Item ID

        Returns:
            tuple: Flask response tuple
        """
        try:
            instance = self.model_class.get_by_id(item_id)
            if not instance:
                return error_response("Item not found", status=404)

            return json_response(data=self.format_response(instance))
        except Exception as e:
            current_app.logger.error(f"Error in get endpoint: {str(e)}")
            return error_response("Failed to fetch item", status=500)

    def handle_update(self, item_id: Union[int, str]) -> tuple:
        """
        Handle PUT/PATCH request for updating an item.

        Args:
            item_id (Union[int, str]): Item ID

        Returns:
            tuple: Flask response tuple
        """
        try:
            instance = self.model_class.get_by_id(item_id)
            if not instance:
                return error_response("Item not found", status=404)

            data = request.get_json()
            if not data:
                return error_response("No data provided", status=400)

            # Validate request data
            errors = self.validate_request(data)
            if errors:
                return error_response("Validation failed", errors=errors, status=400)

            # Update instance
            instance.update(**data)
            return json_response(
                data=self.format_response(instance), message="Item updated successfully"
            )
        except Exception as e:
            current_app.logger.error(f"Error in update endpoint: {str(e)}")
            return error_response("Failed to update item", status=500)

    def handle_delete(self, item_id: Union[int, str]) -> tuple:
        """
        Handle DELETE request for removing an item.

        Args:
            item_id (Union[int, str]): Item ID

        Returns:
            tuple: Flask response tuple
        """
        try:
            instance = self.model_class.get_by_id(item_id)
            if not instance:
                return error_response("Item not found", status=404)

            instance.delete()
            return json_response(message="Item deleted successfully")
        except Exception as e:
            current_app.logger.error(f"Error in delete endpoint: {str(e)}")
            return error_response("Failed to delete item", status=500)


def api_endpoint(model_class: Type[T]):
    """
    Decorator to create RESTful API endpoints for a model.

    Args:
        model_class (Type[T]): The SQLAlchemy model class to use

    Returns:
        Callable: Decorated function that returns APIEndpoint instance
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            endpoint = APIEndpoint(model_class)
            return f(endpoint, *args, **kwargs)

        return wrapper

    return decorator
