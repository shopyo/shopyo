"""
Token purpose separation and single-use guarantees for password reset.

- confirmation tokens must never verify as password-reset tokens (and
  vice versa): distinct serializer salts per purpose
- reset tokens must stop working once the password changes: the payload
  is bound to a fingerprint of the current password hash
"""

import pytest
from shopyo_auth.models import User


@pytest.mark.usefixtures("flask_app")
class TestTokenPurposeSeparation:
    def test_confirmation_token_rejected_by_reset_verifier(self, active_user):
        user = active_user(email="salt-reset@auth.com")
        token = user.generate_confirmation_token()

        assert User.verify_reset_password_token(token) is None

    def test_reset_token_rejected_by_confirmation_verifier(self, active_user):
        user = active_user(email="salt-confirm@auth.com", is_email_confirmed=False)
        token = user.generate_reset_password_token()

        assert user.confirm_token(token) is False
        assert user.is_email_confirmed is False

    def test_confirmation_roundtrip_still_works(self, active_user):
        user = active_user(email="confirm-ok@auth.com", is_email_confirmed=False)
        token = user.generate_confirmation_token()

        assert user.confirm_token(token) is True
        assert user.is_email_confirmed is True

    def test_reset_roundtrip_still_works(self, active_user):
        user = active_user(email="reset-ok@auth.com")
        token = user.generate_reset_password_token()

        verified = User.verify_reset_password_token(token)
        assert verified is not None
        assert verified.id == user.id


@pytest.mark.usefixtures("flask_app")
class TestResetTokenSingleUse:
    def test_token_stops_working_after_password_change(self, active_user):
        user = active_user(email="single-use@auth.com")
        token = user.generate_reset_password_token()
        assert User.verify_reset_password_token(token) is not None

        # the reset (or any other password change) invalidates the token
        user.password = "ANewPass1234!@#$"
        user.update()

        assert User.verify_reset_password_token(token) is None

    def test_fresh_token_valid_after_password_change(self, active_user):
        user = active_user(email="refresh@auth.com")
        stale = user.generate_reset_password_token()

        user.password = "ANewPass1234!@#$"
        user.update()

        assert User.verify_reset_password_token(stale) is None
        fresh = user.generate_reset_password_token()
        assert User.verify_reset_password_token(fresh) is not None

    def test_bare_email_payload_rejected(self, active_user):
        # anything that is not the structured payload (e.g. a legacy
        # plain-email token minted under the same salt) must be refused
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer
        from shopyo_auth.models import RESET_TOKEN_SALT
        from shopyo_auth.models import _token_salt

        user = active_user(email="legacy@auth.com")
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        legacy = serializer.dumps(user.email, salt=_token_salt(RESET_TOKEN_SALT))

        assert User.verify_reset_password_token(legacy) is None
