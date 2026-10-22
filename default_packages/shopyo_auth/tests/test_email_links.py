"""
Outbound email links must use the configured APP_URL.

Without APP_URL the links inherit the request Host header, which a
client controls: a poisoned Host would put attacker-controlled links
into password-reset / confirmation emails.
"""

from unittest.mock import patch

import pytest
from flask import render_template
from flask import url_for
from shopyo_auth import limiter
from shopyo_auth.models import User


@pytest.mark.usefixtures("flask_app")
class TestEmailLinksUseAppUrl:
    def _capture_emails(self, test_client, monkeypatch, flask_app):
        """POST to ``view`` with APP_URL set; return captured templates."""
        monkeypatch.setitem(flask_app.config, "APP_URL", "https://phish-proof.example")
        # the limiter is a process-wide singleton other tests may enable
        monkeypatch.setattr(limiter, "enabled", False)

        captured = []

        def fake_send(to, subject, template, **kwargs):
            captured.append(
                {
                    "to": to,
                    "txt": render_template(f"{template}.txt", **kwargs),
                    "html": render_template(f"{template}.html", **kwargs),
                }
            )

        return captured, fake_send

    def test_reset_email_link_uses_app_url(
        self, test_client, active_user, flask_app, monkeypatch
    ):
        user = active_user(email="links-reset@auth.com")
        captured, fake_send = self._capture_emails(test_client, monkeypatch, flask_app)

        with patch("shopyo_auth.view.send_async_email", side_effect=fake_send):
            response = test_client.post(
                url_for("shopyo_auth.forgot_password"),
                data={"email": user.email},
                follow_redirects=True,
            )
        assert response.status_code == 200

        assert len(captured) == 1
        link = "https://phish-proof.example/shopyo-auth/reset-password/"
        assert link in captured[0]["txt"]
        assert link in captured[0]["html"]
        # the request host must not leak into the email
        assert "localhost" not in captured[0]["txt"]

    def test_confirmation_email_link_uses_app_url(
        self, test_client, flask_app, monkeypatch
    ):
        captured, fake_send = self._capture_emails(test_client, monkeypatch, flask_app)

        with patch("shopyo_auth.view.send_async_email", side_effect=fake_send):
            response = test_client.post(
                url_for("shopyo_auth.register"),
                data={
                    "email": "links-confirm@auth.com",
                    "password": "Pass1234!@#$",
                    "confirm": "Pass1234!@#$",
                },
                follow_redirects=True,
            )
        assert response.status_code == 200

        assert len(captured) == 1
        link = "https://phish-proof.example/shopyo-auth/confirm/"
        assert link in captured[0]["txt"]
        assert link in captured[0]["html"]

        user = User.get_by_email("links-confirm@auth.com")
        assert user is not None
