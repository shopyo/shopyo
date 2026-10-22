"""
Password changes must kill every existing login: sessions and
remember-me cookies alike.

Flask-Login's identity (``User.get_id()``) embeds the password state —
``"<id>|<stamp>"``. login_user stores it in the session, remember-me
cookies carry it verbatim (the cookie payload is exactly get_id()), and
load_user re-verifies the stamp on every load. Stale identities and
bare ids without any credential state are refused.
"""

import pytest
from flask import g
from flask import url_for
from flask_login.utils import encode_cookie
from init import db


def _clear_login_cache():
    """Make the next request run the user loader.

    The shared app-context fixture keeps one Flask/g context alive for
    the whole test, and flask_login caches the loaded user on g. In
    production every request gets a fresh context and the loader runs on
    every request; clear the cache here to reproduce that.
    """
    if hasattr(g, "_login_user"):
        del g._login_user


def _login_session(test_client, user):
    """Put into the session exactly what login_user writes.

    The HTTP login route is avoided on purpose: the in-memory rate
    limiter is a process-wide singleton that other tests exhaust.
    """
    with test_client.session_transaction() as sess:
        sess["_user_id"] = user.get_id()


def _get_tokens(test_client):
    _clear_login_cache()
    return test_client.get(url_for("shopyo_auth.list_tokens"))


@pytest.mark.usefixtures("flask_app")
class TestPasswordChangeInvalidatesLogins:
    def test_session_dies_when_password_changes(self, test_client, active_user):
        user = active_user(email="sess-die@auth.com", password="Pass1234!@#$")
        _login_session(test_client, user)

        # authenticated while the password is unchanged
        assert _get_tokens(test_client).status_code == 200

        # owner (or admin CLI) changes the password elsewhere
        user.password = "ANewPass1234!@#$"
        db.session.commit()

        # the pre-change session is now refused
        response = _get_tokens(test_client)
        assert response.status_code in (302, 401)
        if response.status_code == 302:
            assert "login" in response.headers["Location"]

        # logging in again with the new password restores access
        _login_session(test_client, user)
        assert _get_tokens(test_client).status_code == 200

    def test_session_survives_without_password_change(self, test_client, active_user):
        user = active_user(email="sess-live@auth.com", password="Pass1234!@#$")
        _login_session(test_client, user)

        for _ in range(2):
            assert _get_tokens(test_client).status_code == 200

    def test_bare_identity_is_refused(self, test_client, active_user):
        # ids without credential state (legacy sessions, hand-built
        # sessions) cannot be verified -> forced re-login
        user = active_user(email="sess-bare@auth.com", password="Pass1234!@#$")

        with test_client.session_transaction() as sess:
            sess["_user_id"] = user.id

        assert _get_tokens(test_client).status_code in (302, 401)

    def test_remember_cookie_dies_when_password_changes(
        self, flask_app, active_user
    ):
        user = active_user(email="remember@auth.com", password="Pass1234!@#$")
        # flask_login's remember path signs get_id() into the cookie and
        # later feeds the decoded payload straight into the loader
        cookie = encode_cookie(user.get_id())
        client = flask_app.test_client()
        client.set_cookie("remember_token", cookie, domain="localhost.com")

        # the remembered login works while the password is unchanged
        assert _get_tokens(client).status_code == 200

        user.password = "ANewPass1234!@#$"
        db.session.commit()

        # the pre-change cookie is refused from then on
        assert _get_tokens(client).status_code in (302, 401)
