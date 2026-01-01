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
        # Safe internal URLs
        assert security.is_safe_redirect_url("/home")
        assert security.is_safe_redirect_url("http://example.com/home")

        # Unsafe external URLs
        assert not security.is_safe_redirect_url("http://evil.com")
        assert not security.is_safe_redirect_url("ftp://example.com")


def test_get_safe_redirect(app):
    with app.test_request_context(base_url="http://example.com"):
        # Valid URL
        assert security.get_safe_redirect("/home") == "/home"

        # Invalid URL -> fallback to root
        assert security.get_safe_redirect("http://evil.com") == "/"


def test_csrf_token_generation(app):
    with app.test_request_context():
        # First call generates token
        token1 = security.generate_csrf_token()
        assert token1
        assert session[security.CSRF_TOKEN_SESSION_KEY] == token1

        # Second call returns same token
        token2 = security.generate_csrf_token()
        assert token1 == token2


def test_csrf_token_validation(app):
    with app.test_request_context():
        token = security.generate_csrf_token()

        assert security.validate_csrf_token(token)
        assert not security.validate_csrf_token("invalid-token")
        assert not security.validate_csrf_token(None)


def test_inject_csrf_token(app):
    with app.test_request_context():
        context = security.inject_csrf_token()
        assert security.CSRF_TOKEN_FORM_KEY in context
        assert (
            context[security.CSRF_TOKEN_FORM_KEY]
            == session[security.CSRF_TOKEN_SESSION_KEY]
        )


def test_csrf_protect(app):
    @app.route("/protected", methods=["POST"])
    @security.csrf_protect
    def protected():
        return "OK"

    client = app.test_client()

    # Fail without token
    response = client.post("/protected")
    assert response.status_code == 403

    # Success with token
    with client.session_transaction() as sess:
        sess[security.CSRF_TOKEN_SESSION_KEY] = "test-token"

    response = client.post("/protected", data={"csrf_token": "test-token"})
    assert response.status_code == 200
