import pytest
from flask import url_for
from shopyo_auth.models import User


def test_events_triggered(test_client, flask_app):
    auth = flask_app.extensions["shopyo_auth"]

    events_called = []

    @auth.on("user_registered")
    def on_reg(user):
        events_called.append("registered")

    @auth.on("user_login")
    def on_login(user):
        events_called.append("login")

    @auth.on("user_logout")
    def on_logout(user):
        events_called.append("logout")

    # 1. Test Registration Event
    data = {
        "email": "event@example.com",
        "password": "Pass1234!@#$",
        "confirm": "Pass1234!@#$",
        "csrf_token": "",
    }
    test_client.post(url_for("shopyo_auth.register"), data=data)
    assert "registered" in events_called

    # 2. Test Login Event
    events_called = []
    test_client.post(
        url_for("shopyo_auth.login"),
        data={
            "email": "event@example.com",
            "password": "Pass1234!@#$",
            "csrf_token": "",
        },
    )
    assert "login" in events_called

    # 3. Test Logout Event
    events_called = []
    test_client.get(url_for("shopyo_auth.logout"))
    assert "logout" in events_called


def test_password_events(test_client, flask_app):
    auth = flask_app.extensions["shopyo_auth"]
    events_called = []

    @auth.on("password_reset_requested")
    def on_req(user):
        events_called.append("requested")

    @auth.on("password_reset_completed")
    def on_comp(user):
        events_called.append("completed")

    with flask_app.app_context():
        user = User.create(email="pw-event@example.com", password="Pass1234!@#$")

        # Request reset
        test_client.post(
            url_for("shopyo_auth.forgot_password"),
            data={"email": "pw-event@example.com", "csrf_token": ""},
        )
        assert "requested" in events_called

        # Complete reset
        token = user.generate_reset_password_token()
        test_client.post(
            url_for("shopyo_auth.reset_password", token=token),
            data={
                "password": "NewPass1234!@#$",
                "confirm": "NewPass1234!@#$",
                "csrf_token": "",
            },
        )
        assert "completed" in events_called
