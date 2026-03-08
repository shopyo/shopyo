import pytest
from flask import url_for
from shopyo_auth import limiter


def test_ratelimit_disabled(test_client, flask_app):
    flask_app.config["SHOPYO_AUTH_RATE_LIMIT_ENABLED"] = False
    # If disabled, limiter.init_app is not called in ShopyoAuth.init_app
    # based on my current implementation

    # Should be able to hit many times
    for _ in range(10):
        response = test_client.get(url_for("shopyo_auth.login"))
        assert response.status_code == 200


def test_ratelimit_enabled(test_client, flask_app):
    flask_app.config["SHOPYO_AUTH_RATE_LIMIT_ENABLED"] = True
    # We might need to manually trigger init_app if the fixture app was already created
    # but the fixture re-creates it usually.

    with flask_app.app_context():
        limiter.storage.reset()

    # Hit 5 times (default limit)
    for _ in range(5):
        response = test_client.get(url_for("shopyo_auth.login"))
        assert response.status_code == 200

    # 6th time should fail
    response = test_client.get(url_for("shopyo_auth.login"))
    assert response.status_code == 429
    assert (
        b"Too many requests" in response.data or b"Rate limit exceeded" in response.data
    )


def test_ratelimit_per_endpoint(test_client, flask_app):
    flask_app.config["SHOPYO_AUTH_RATE_LIMIT_ENABLED"] = True
    with flask_app.app_context():
        limiter.storage.reset()

    # Exhaust login
    for _ in range(5):
        test_client.get(url_for("shopyo_auth.login"))

    assert test_client.get(url_for("shopyo_auth.login")).status_code == 429

    # register should still be fine
    assert test_client.get(url_for("shopyo_auth.register")).status_code == 200
