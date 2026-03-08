"""
Elite Tests for Auth Events.
Verifies synchronous hooks for lifecycle observability.
"""

import pytest
from flask import url_for
from shopyo_auth.models import User


class TestAuthEvents:
    """Verifies all core events are triggered with correct context."""

    def test_lifecycle_events(self, test_client, auth_ext, flask_app):
        """Verify registration, login, and logout events."""
        called = []

        @auth_ext.on("user_registered")
        def on_reg(user):
            called.append("reg")

        @auth_ext.on("user_login")
        def on_login(user):
            called.append("login")

        @auth_ext.on("user_logout")
        def on_logout(user):
            called.append("logout")

        # 1. Registration
        test_client.post(
            url_for("shopyo_auth.register"),
            data={
                "email": "event-test@auth.com",
                "password": "Pass1234!@#$",
                "confirm": "Pass1234!@#$",
            },
        )
        assert "reg" in called

        # 2. Login
        called = []
        test_client.post(
            url_for("shopyo_auth.login"),
            data={
                "email": "event-test@auth.com",
                "password": "Pass1234!@#$",
            },
        )
        assert "login" in called

        # 3. Logout
        called = []
        test_client.get(url_for("shopyo_auth.logout"))
        assert "logout" in called

    def test_password_events(self, test_client, auth_ext, active_user):
        """Verify password reset request and completion events."""
        called = []

        @auth_ext.on("password_reset_requested")
        def on_req(user):
            called.append("req")

        @auth_ext.on("password_reset_completed")
        def on_comp(user):
            called.append("comp")

        user = active_user(email="pw-events@auth.com")

        # Request
        test_client.post(
            url_for("shopyo_auth.forgot_password"), data={"email": user.email}
        )
        assert "req" in called

        # Complete
        token = user.generate_reset_password_token()
        test_client.post(
            url_for("shopyo_auth.reset_password", token=token),
            data={
                "password": "NewStrongPass1234!",
                "confirm": "NewStrongPass1234!",
            },
        )
        assert "comp" in called
