import pytest
from flask import Flask
from shopyo.api.assets import get_static, register_devstatic


def test_get_static_debug_true():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["SERVER_NAME"] = "localhost"
    register_devstatic(app, "/tmp/modules")
    with app.app_context():
        with app.test_request_context():
            url = get_static("box__default/auth", "style.css")
            assert "/devstatic/box__default/auth/f/style.css" in url


def test_get_static_debug_false():
    app = Flask(__name__)
    app.config["DEBUG"] = False
    app.config["SERVER_NAME"] = "localhost"
    with app.app_context():
        with app.test_request_context():
            url = get_static("box__default/auth", "style.css")
            assert "/static/modules/box__default/auth/style.css" in url
