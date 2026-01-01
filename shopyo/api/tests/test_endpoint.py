import pytest
from flask import Flask, request
from shopyo.api.endpoint import APIEndpoint, api_endpoint
from shopyo.api.models import PkModel
from init import db


class EndpointModelForTesting(PkModel):
    __tablename__ = "test_endpoint_model_unique"
    name = db.Column(db.String(50))


class MockEndpoint(APIEndpoint):
    def format_response(self, data):
        if isinstance(data, list):
            return [{"id": item.id, "name": item.name} for item in data]
        return {"id": data.id, "name": data.name}


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

        # Success
        res, status = endpoint.handle_get(item.id)
        assert status == 200
        assert res.get_json()["data"]["name"] == "Test Item"

        # Not found
        res, status = endpoint.handle_get(999)
        assert status == 404


def test_handle_create(app, model_class):
    with app.test_request_context(json={"name": "New Item"}):
        endpoint = MockEndpoint(model_class)
        res, status = endpoint.handle_create()
        assert status == 201
        assert res.get_json()["data"]["name"] == "New Item"
        assert model_class.query.count() == 1


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


def test_handle_update(app, model_class):
    with app.app_context():
        item = model_class.create(name="Old Name")

        with app.test_request_context(json={"name": "New Name"}):
            endpoint = MockEndpoint(model_class)
            res, status = endpoint.handle_update(item.id)
            assert status == 200
            assert res.get_json()["data"]["name"] == "New Name"
            assert model_class.get_by_id(item.id).name == "New Name"


def test_handle_delete(app, model_class):
    with app.app_context():
        item = model_class.create(name="To Delete")
        endpoint = MockEndpoint(model_class)
        res, status = endpoint.handle_delete(item.id)
        assert status == 200
        assert model_class.query.count() == 0


def test_api_endpoint_decorator(app, model_class):
    @api_endpoint(model_class)
    def my_view(endpoint, item_id):
        # Override format_response for the decorated endpoint if needed
        # but here we can just mock the return
        endpoint.format_response = lambda data: {"name": data.name}
        return endpoint.handle_get(item_id)

    with app.app_context():
        item = model_class.create(name="Decorated")
        res, status = my_view(item.id)
        assert status == 200
        assert res.get_json()["data"]["name"] == "Decorated"
