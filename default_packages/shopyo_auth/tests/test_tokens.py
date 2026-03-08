"""
Elite Tests for API Tokens (Personal Access Tokens).
Verifies lifecycle, authentication, and automatic revocation on security events.
"""

import pytest
from shopyo_auth.models import User, UserToken
from flask import url_for


class TestAPITokens:
    """Verifies the complete token lifecycle."""

    def test_api_token_lifecycle(self, test_client, active_user):
        """Verify token creation, usage, and manual deletion."""
        user = active_user(email="token-lifecycle@auth.com")

        # 1. Create token
        with test_client.session_transaction() as sess:
            sess["_user_id"] = user.id

        response = test_client.post(
            url_for("shopyo_auth.create_token"), json={"name": "test-token"}
        )
        assert response.status_code == 201
        raw_token = response.get_json()["token"]

        # 2. Use token
        response = test_client.get(
            "/api/test-protected", headers={"Authorization": f"Bearer {raw_token}"}
        )
        assert response.status_code == 200
        assert response.get_json()["user"] == user.email

        # 3. Delete token
        token_id = user.tokens.first().id
        response = test_client.delete(
            url_for("shopyo_auth.delete_token", token_id=token_id)
        )
        assert response.status_code == 200

        # Should now fail
        assert (
            test_client.get(
                "/api/test-protected", headers={"Authorization": f"Bearer {raw_token}"}
            ).status_code
            == 401
        )

    def test_token_auto_revocation(self, active_user):
        """Verify tokens are revoked automatically when password changes."""
        user = active_user(email="revoke@auth.com")
        token = user.generate_api_token("vulnerable")
        from init import db

        db.session.commit()

        assert User.verify_api_token(token) is not None

        # Security Event: Password Change
        user.password = "NewStrongPass1234!"
        user.update()

        # Token must be invalid
        assert User.verify_api_token(token) is None
        assert user.tokens.count() == 0

    def test_token_hashing(self, active_user):
        """Verify tokens are never stored in plaintext."""
        user = active_user()
        token = user.generate_api_token("secret")
        from init import db

        db.session.commit()

        db_token = UserToken.query.filter_by(user_id=user.id).first()
        assert db_token.token_hash != token
        assert len(db_token.token_hash) == 64  # SHA-256
