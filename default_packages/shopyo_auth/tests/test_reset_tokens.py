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
