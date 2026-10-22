"""
Existing login sessions must not survive a password change.

The user loader compares a session stamp captured at login time against
the user's current password state; a mismatch (password changed after
the session was created) forces a re-login.
"""

import pytest
from flask import g
from flask import url_for
from init import db
from shopyo_auth.models import PWD_CHANGE_SESSION_KEY


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
    """Put into the session exactly what the login view does.

    The HTTP login route is avoided on purpose: the in-memory rate
    limiter is a process-wide singleton that other tests exhaust.
    """
    with test_client.session_transaction() as sess:
        sess["_user_id"] = user.id
        sess[PWD_CHANGE_SESSION_KEY] = user.password_stamp()


def _get_tokens(test_client):
    _clear_login_cache()
    return test_client.get(url_for("shopyo_auth.list_tokens"))


@pytest.mark.usefixtures("flask_app")
class TestSessionInvalidationOnPasswordChange:
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

    def test_unstamped_session_is_pinned_then_invalidated(
        self, test_client, active_user
    ):
        # legacy / remember-me sessions carry no stamp: they work, but
        # become pinned to the current password state on first use
        user = active_user(email="sess-pin@auth.com", password="Pass1234!@#$")

        with test_client.session_transaction() as sess:
            sess["_user_id"] = user.id

        assert _get_tokens(test_client).status_code == 200

        with test_client.session_transaction() as sess:
            assert PWD_CHANGE_SESSION_KEY in sess

        user.password = "ANewPass1234!@#$"
        db.session.commit()

        assert _get_tokens(test_client).status_code in (302, 401)
