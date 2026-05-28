import pytest
from flask import Flask, request
from shopyo.api.endpoint import APIEndpoint, api_endpoint
from shopyo.api.models import PkModel, SearchMixin
from init import db


class EndpointModelForTesting(PkModel):
    __tablename__ = "test_endpoint_model_unique"
    name = db.Column(db.String(50))
    title = db.Column(db.String(50))


class SearchableEndpointModel(PkModel, SearchMixin):
    __tablename__ = "searchable_test_model"
    name = db.Column(db.String(50))
    description = db.Column(db.String(100))


class MockEndpoint(APIEndpoint):
    def format_response(self, data):
        if isinstance(data, list):
            return [{"id": item.id, "name": item.name} for item in data]
        return {"id": data.id, "name": data.name}


class ValidatingEndpoint(MockEndpoint):
    def validate_request(self, data):
        errors = []
        if not data.get("name"):
            errors.append("name is required")
        return errors


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
    return EndpointModelForTesting


def test_handle_get(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test Item")
        endpoint = MockEndpoint(model_class)

        res, status = endpoint.handle_get(item.id)
        assert status == 200
        assert res.get_json()["data"]["name"] == "Test Item"

        res, status = endpoint.handle_get(999)
        assert status == 404


def test_handle_create(app, model_class):
    with app.test_request_context(json={"name": "New Item"}):
        endpoint = MockEndpoint(model_class)
        res, status = endpoint.handle_create()
        assert status == 201
        assert res.get_json()["data"]["name"] == "New Item"
        assert model_class.query.count() == 1


def test_handle_create_no_data(app, model_class):
    with app.test_request_context(data="{}", content_type="application/json"):
        endpoint = MockEndpoint(model_class)
        res, status = endpoint.handle_create()
        assert status == 400
        assert "No data provided" in res.get_json()["error"]["message"]


def test_handle_create_validation_error(app, model_class):
    with app.test_request_context(json={"name": ""}):
        endpoint = ValidatingEndpoint(model_class)
        res, status = endpoint.handle_create()
        assert status == 400
        assert "Validation failed" in res.get_json()["error"]["message"]


def test_handle_list(app, model_class):
    with app.app_context():
        model_class.create(name="Item 1")
        model_class.create(name="Item 2")

        with app.test_request_context():
            endpoint = MockEndpoint(model_class)
            res, status = endpoint.handle_list()
            assert status == 200
            json_data = res.get_json()
            assert len(json_data["data"]) == 2
            assert json_data["pagination"]["total"] == 2


def test_handle_list_with_search(app, model_class):
    with app.app_context():
        model_class.create(name="Alpha")
        model_class.create(name="Beta")

        with app.test_request_context(query_string={"search": "Alpha"}):
            endpoint = MockEndpoint(model_class)
            res, status = endpoint.handle_list()
            assert status == 200
            # model doesn't have a search classmethod, so all items returned
            assert res.get_json()["pagination"]["total"] == 2


def test_handle_list_with_search_in_searchable(app):
    with app.app_context():
        db.create_all()
        SearchableEndpointModel.create(name="Alpha", description="First")
        SearchableEndpointModel.create(name="Beta", description="Second")

        with app.test_request_context(query_string={"search": "Alpha"}):
            endpoint = MockEndpoint(SearchableEndpointModel)
            res, status = endpoint.handle_list()
            assert status == 200
            data = res.get_json()
            assert data["pagination"]["total"] >= 1
            # search is enabled, should filter
            names = [item["name"] for item in data["data"]]
            assert "Alpha" in names


def test_handle_list_with_sort(app, model_class):
    with app.app_context():
        model_class.create(name="B", title="x")
        model_class.create(name="A", title="y")

        with app.test_request_context(
            query_string={"sort_by": "name", "order": "desc"}
        ):
            endpoint = MockEndpoint(model_class)
            res, status = endpoint.handle_list()
            assert status == 200
            data = res.get_json()["data"]
            assert data[0]["name"] == "B"

        with app.test_request_context(query_string={"sort_by": "name", "order": "asc"}):
            endpoint = MockEndpoint(model_class)
            res, status = endpoint.handle_list()
            assert status == 200
            data = res.get_json()["data"]
            assert data[0]["name"] == "A"


def test_handle_list_with_sort_invalid_field(app, model_class):
    with app.app_context():
        model_class.create(name="Test")
        with app.test_request_context(query_string={"sort_by": "nonexistent"}):
            endpoint = MockEndpoint(model_class)
            res, status = endpoint.handle_list()
            assert status == 200
            data = res.get_json()["data"]
            assert len(data) == 1


def test_handle_update(app, model_class):
    with app.app_context():
        item = model_class.create(name="Old Name")

        with app.test_request_context(json={"name": "New Name"}):
            endpoint = MockEndpoint(model_class)
            res, status = endpoint.handle_update(item.id)
            assert status == 200
            assert res.get_json()["data"]["name"] == "New Name"
            assert model_class.get_by_id(item.id).name == "New Name"


def test_handle_update_not_found(app, model_class):
    with app.app_context():
        with app.test_request_context(json={"name": "Nope"}):
            endpoint = MockEndpoint(model_class)
            res, status = endpoint.handle_update(999)
            assert status == 404
            assert "Item not found" in res.get_json()["error"]["message"]


def test_handle_update_no_data(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test")

        with app.test_request_context(data="{}", content_type="application/json"):
            endpoint = MockEndpoint(model_class)
            res, status = endpoint.handle_update(item.id)
            assert status == 400
            assert "No data provided" in res.get_json()["error"]["message"]


def test_handle_update_validation_error(app, model_class):
    with app.app_context():
        item = model_class.create(name="Test")

        with app.test_request_context(json={"name": ""}):
            endpoint = ValidatingEndpoint(model_class)
            res, status = endpoint.handle_update(item.id)
            assert status == 400
            assert "Validation failed" in res.get_json()["error"]["message"]


def test_handle_delete(app, model_class):
    with app.app_context():
        item = model_class.create(name="To Delete")
        endpoint = MockEndpoint(model_class)
        res, status = endpoint.handle_delete(item.id)
        assert status == 200
        assert model_class.query.count() == 0


def test_handle_delete_not_found(app, model_class):
    with app.app_context():
        endpoint = MockEndpoint(model_class)
        res, status = endpoint.handle_delete(999)
        assert status == 404
        assert "Item not found" in res.get_json()["error"]["message"]


def test_default_format_response(app, model_class):
    with app.app_context():
        item = model_class.create(name="Direct")
        ep = APIEndpoint(model_class)
        result = ep.format_response(item)
        assert result is item


def test_api_endpoint_decorator(app, model_class):
    @api_endpoint(model_class)
    def my_view(endpoint, item_id):
        endpoint.format_response = lambda data: {"name": data.name}
        return endpoint.handle_get(item_id)

    with app.app_context():
        item = model_class.create(name="Decorated")
        res, status = my_view(item.id)
        assert status == 200
        assert res.get_json()["data"]["name"] == "Decorated"


def test_handle_list_exception(app, model_class):
    with app.app_context():
        with app.test_request_context():
            endpoint = MockEndpoint(model_class)
            with pytest.MonkeyPatch.context() as mp:
                mp.setattr(
                    endpoint,
                    "get_query_filters",
                    lambda: (_ for _ in ()).throw(Exception("boom")),
                )
                res, status = endpoint.handle_list()
                assert status == 500


def test_handle_create_exception(app, model_class):
    with app.test_request_context(json={"name": "Test"}):
        endpoint = MockEndpoint(model_class)
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                model_class,
                "create",
                lambda **kw: (_ for _ in ()).throw(Exception("boom")),
            )
            res, status = endpoint.handle_create()
            assert status == 500


def test_handle_get_exception(app, model_class):
    with app.app_context():
        endpoint = MockEndpoint(model_class)
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                model_class,
                "get_by_id",
                lambda id: (_ for _ in ()).throw(Exception("boom")),
            )
            res, status = endpoint.handle_get(1)
            assert status == 500


def test_handle_update_exception(app, model_class):
    with app.app_context():
        endpoint = MockEndpoint(model_class)
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                model_class,
                "get_by_id",
                lambda id: (_ for _ in ()).throw(Exception("boom")),
            )
            res, status = endpoint.handle_update(1)
            assert status == 500


def test_handle_delete_exception(app, model_class):
    with app.app_context():
        endpoint = MockEndpoint(model_class)
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                model_class,
                "get_by_id",
                lambda id: (_ for _ in ()).throw(Exception("boom")),
            )
            res, status = endpoint.handle_delete(1)
            assert status == 500
