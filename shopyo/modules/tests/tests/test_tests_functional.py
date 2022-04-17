# Please add your functional tests to this file.
from shopyo.api.assets import get_static


def test_static_module(test_client):
    response = test_client.get(get_static("tests", "file.css"))
    assert response.status_code == 200
    assert b"module tests file.css" in response.data


def test_static_box(test_client):
    response = test_client.get(get_static("box__tests/test1", "file.css"))
    assert response.status_code == 200
    assert b"box__tests/tests file.css" in response.data
