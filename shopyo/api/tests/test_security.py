import pytest
from flask import Flask, session
from shopyo.api import security


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "test-key"
    return app


def test_is_safe_redirect_url(app):
    with app.test_request_context(base_url="http://example.com"):
        assert security.is_safe_redirect_url("/home")
        assert security.is_safe_redirect_url("http://example.com/home")
        assert not security.is_safe_redirect_url("http://evil.com")
        assert not security.is_safe_redirect_url("ftp://example.com")


def test_get_safe_redirect(app):
    with app.test_request_context(base_url="http://example.com"):
        assert security.get_safe_redirect("/home") == "/home"
        assert security.get_safe_redirect("http://evil.com") == "/"


class TestCsrfToken:
    def test_generation_persists(self, app):
        with app.test_request_context():
            token1 = security.generate_csrf_token()
            token2 = security.generate_csrf_token()
            assert token1 == token2
            assert session[security.CSRF_TOKEN_SESSION_KEY] == token1

    def test_validation_valid(self, app):
        with app.test_request_context():
            token = security.generate_csrf_token()
            assert security.validate_csrf_token(token) is True

    def test_validation_invalid(self, app):
        with app.test_request_context():
            security.generate_csrf_token()
            assert security.validate_csrf_token("wrong-token") is False

    def test_validation_none(self, app):
        with app.test_request_context():
            security.generate_csrf_token()
            assert security.validate_csrf_token(None) is False
            assert security.validate_csrf_token("") is False

    def test_validation_no_session_token(self, app):
        with app.test_request_context():
            assert security.validate_csrf_token("some-token") is False

    def test_inject_csrf_token(self, app):
        with app.test_request_context():
            context = security.inject_csrf_token()
            assert security.CSRF_TOKEN_FORM_KEY in context
            assert (
                context[security.CSRF_TOKEN_FORM_KEY]
                == session[security.CSRF_TOKEN_SESSION_KEY]
            )

    def test_generates_on_first_call(self, app):
        with app.test_request_context():
            token = security.generate_csrf_token()
            assert len(token) > 0
            assert token != ""

    def test_validate_constant_time_not_crash(self, app):
        with app.test_request_context():
            security.generate_csrf_token()
            assert security.validate_csrf_token("a" * 128) is False
            assert security.validate_csrf_token("b" * 256) is False
