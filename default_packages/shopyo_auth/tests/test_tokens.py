import pytest
from flask import url_for, g
from shopyo_auth.models import User, UserToken
from shopyo_auth.decorators import token_required


def test_api_token_lifecycle(test_client, flask_app):
    with flask_app.app_context():
        user = User.create(email="tokenuser@example.com", password="Pass1234!@#$")

        # 1. Create token
        # Mock login
        with test_client.session_transaction() as sess:
            sess["_user_id"] = user.id

        response = test_client.post(
            url_for("shopyo_auth.create_token"), json={"name": "test-token"}
        )
        assert response.status_code == 201
        token_data = response.get_json()
        assert "token" in token_data
        raw_token = token_data["token"]

        # 2. List tokens
        response = test_client.get(url_for("shopyo_auth.list_tokens"))
        assert response.status_code == 200
        tokens = response.get_json()
        assert len(tokens) == 1
        assert tokens[0]["name"] == "test-token"
        token_id = tokens[0]["id"]

        # 3. Use token
        @flask_app.route("/api/test-protected")
        @token_required
        def protected():
            return {"user": g.current_user.email}

        # Success with token
        response = test_client.get(
            "/api/test-protected", headers={"Authorization": f"Bearer {raw_token}"}
        )
        assert response.status_code == 200
        assert response.get_json()["user"] == "tokenuser@example.com"

        # Fail with invalid token
        response = test_client.get(
            "/api/test-protected", headers={"Authorization": "Bearer invalid"}
        )
        assert response.status_code == 401

        # 4. Delete token
        response = test_client.delete(
            url_for("shopyo_auth.delete_token", token_id=token_id)
        )
        assert response.status_code == 200

        # Use deleted token - should fail
        response = test_client.get(
            "/api/test-protected", headers={"Authorization": f"Bearer {raw_token}"}
        )
        assert response.status_code == 401


def test_token_invalidation_on_password_change(test_client, flask_app):
    with flask_app.app_context():
        user = User.create(email="changepass@example.com", password="OldPass1234!@#$")
        raw_token = user.generate_api_token("vulnerable-token")

        # Token works initially
        assert User.verify_api_token(raw_token) is not None

        # Change password
        user.password = "NewPass1234!@#$"
        user.update()

        # Token should now be invalid because it's deleted
        assert User.verify_api_token(raw_token) is None
        assert UserToken.query.filter_by(user_id=user.id).count() == 0


def test_user_model_token_methods(flask_app):
    with flask_app.app_context():
        user = User.create(email="methods@example.com", password="Pass1234!@#$")
        token = user.generate_api_token("test")

        verified_user = User.verify_api_token(token)
        assert verified_user.id == user.id

        # Test hash storage
        db_token = UserToken.query.filter_by(user_id=user.id).first()
        assert db_token.token_hash != token  # Should be hashed
