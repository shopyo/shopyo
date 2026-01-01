import pytest
from flask import Flask
from shopyo.api import response


@pytest.fixture
def app():
    app = Flask(__name__)
    return app


def test_json_response(app):
    with app.test_request_context():
        res, status = response.json_response(data={"id": 1}, message="Success")
        assert status == 200
        json_data = res.get_json()
        assert json_data["success"] is True
        assert json_data["data"] == {"id": 1}
        assert json_data["message"] == "Success"


def test_error_response(app):
    with app.test_request_context():
        res, status = response.error_response(
            message="Bad Request", status=400, errors={"field": "required"}
        )
        assert status == 400
        json_data = res.get_json()
        assert json_data["success"] is False
        assert json_data["error"]["message"] == "Bad Request"
        assert json_data["error"]["details"] == {"field": "required"}


def test_paginated_response(app):
    with app.test_request_context():
        items = [1, 2, 3]
        res, status = response.paginated_response(
            items=items, total=10, page=1, per_page=3
        )
        assert status == 200
        json_data = res.get_json()
        assert json_data["success"] is True
        assert json_data["data"] == items
        assert json_data["pagination"]["total"] == 10
        assert json_data["pagination"]["page"] == 1
        assert json_data["pagination"]["per_page"] == 3
        assert json_data["pagination"]["pages"] == 4
