import pytest
from flask import Flask
from shopyo.api.models import (
    PkModel,
    TimestampMixin,
    SoftDeleteMixin,
    SearchMixin,
    PaginationMixin,
    ValidationMixin,
    YoModel,
)
from init import db


class FullModel(PkModel, TimestampMixin, SoftDeleteMixin, SearchMixin, PaginationMixin):
    __tablename__ = "test_model_unique"
    name = db.Column(db.String(50))
    description = db.Column(db.String(100))


class SimpleModel(PkModel):
    name = db.Column(db.String(50))


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
    return FullModel


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


def test_crud_update_no_commit(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test")
        result = item.update(commit=False, name="NoCommit")
        assert result is None
        assert item.name == "NoCommit"


def test_crud_delete(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test")
        item_id = item.id
        item.delete()
        assert model_class.get_by_id(item_id) is None


def test_crud_delete_no_commit(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test")
        result = item.delete(commit=False)
        assert result is None


def test_save_no_commit(app, model_class):
    with app.app_context():
        item = model_class(name="Unsaved")
        result = item.save(commit=False)
        # session is dirty but not committed
        assert result == item


def test_soft_delete(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test")
        item.soft_delete()
        assert item.is_deleted is True
        assert model_class.get_active().count() == 0


def test_soft_delete_no_commit(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test")
        result = item.soft_delete(commit=False)
        assert result is None
        assert item.is_deleted is True


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
        assert model_class.get_by_id(float(item.id)) == item


def test_get_or_404_found(app, model_class):
    with app.app_context():
        item = model_class.create(name="Found")
        result = model_class.get_or_404(item.id)
        assert result == item


def test_get_or_404_not_found(app, model_class):
    with app.app_context():
        from werkzeug.exceptions import NotFound

        with pytest.raises(NotFound):
            model_class.get_or_404(999)


def test_bulk_create(app, model_class):
    with app.app_context():
        items = model_class.bulk_create(
            [
                {"name": "A", "description": "First"},
                {"name": "B", "description": "Second"},
            ]
        )
        assert model_class.query.count() == 2


def test_validation_mixin():
    class TestValid(ValidationMixin):
        pass

    obj = TestValid()
    assert obj.validate() == []
    assert obj.is_valid() is True


def test_repr(app, model_class):
    with app.app_context():
        item = model_class.create(name="ReprTest")
        assert repr(item) == f"<{model_class.__name__} id={item.id}>"


def test_yomodel_tablename(app):
    with app.app_context():
        assert SimpleModel.__tablename__ == "simplemodel"
