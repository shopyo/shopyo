"""Tests for absolute_url: host-stable absolute URLs for outbound links."""

from flask import Flask

from shopyo.api.urls import absolute_url


def _make_app():
    app = Flask(__name__)
    app.add_url_rule("/hello", "hello", lambda: "hi")
    return app


def test_absolute_url_uses_app_url_config():
    app = _make_app()
    app.config["APP_URL"] = "https://good.example"

    with app.test_request_context("/", base_url="http://evil.example/"):
        assert absolute_url("hello") == "https://good.example/hello"


def test_absolute_url_strips_trailing_slash_from_app_url():
    app = _make_app()
    app.config["APP_URL"] = "https://good.example/"

    with app.test_request_context("/", base_url="http://evil.example/"):
        assert absolute_url("hello") == "https://good.example/hello"


def test_absolute_url_falls_back_to_request_host():
    app = _make_app()

    with app.test_request_context("/", base_url="http://dev.example/"):
        assert absolute_url("hello") == "http://dev.example/hello"


def test_absolute_url_honours_server_name():
    app = _make_app()
    app.config["SERVER_NAME"] = "canonical.example"

    with app.test_request_context("/"):
        assert absolute_url("hello") == "http://canonical.example/hello"
