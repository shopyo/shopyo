import pytest
from flask import Flask
from shopyo.api.models import (
    PkModel,
    TimestampMixin,
    SoftDeleteMixin,
    SearchMixin,
    PaginationMixin,
)
from init import db


class ModelForTesting(
    PkModel, TimestampMixin, SoftDeleteMixin, SearchMixin, PaginationMixin
):
    __tablename__ = "test_model_unique"
    name = db.Column(db.String(50))
    description = db.Column(db.String(100))


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def model_class():
    return ModelForTesting


def test_crud_create(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test", description="Desc")
        assert item.id is not None
        assert item.name == "Test"
        assert item.created_at is not None
        assert item.updated_at is not None


def test_crud_update(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test")
        item.update(name="Updated")
        assert item.name == "Updated"


def test_crud_delete(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test")
        item_id = item.id
        item.delete()
        assert model_class.get_by_id(item_id) is None


def test_soft_delete(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test")
        item.soft_delete()
        assert item.is_deleted is True
        assert model_class.get_active().count() == 0


def test_search(app, model_class):
    with app.app_context():
        model_class.create(name="Apple", description="Fruit")
        model_class.create(name="Banana", description="Fruit")

        results = model_class.search("Apple", ["name"]).all()
        assert len(results) == 1
        assert results[0].name == "Apple"

        results = model_class.search("Fruit", ["description"]).all()
        assert len(results) == 2


def test_pagination(app, model_class):
    with app.app_context():
        for i in range(10):
            model_class.create(name=f"Item {i}")

        paginated = model_class.paginate(page=1, per_page=5)
        assert len(paginated["items"]) == 5
        assert paginated["total"] == 10
        assert paginated["pages"] == 2


def test_get_by_id(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test")
        assert model_class.get_by_id(item.id) == item
        assert model_class.get_by_id(str(item.id)) == item
        assert model_class.get_by_id("invalid") is None
