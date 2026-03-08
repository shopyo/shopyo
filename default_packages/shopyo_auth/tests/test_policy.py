"""
Elite Tests for Policy and Authorization.
Verifies granular access control using the unified @require decorator and g.current_user.
"""

import pytest
from shopyo_auth.models import User, Role
from flask import g


class TestAuthorization:
    """Verifies access control across admin, roles, and policies."""

    def test_require_admin_only(self, test_client, active_user, flask_app):
        """Admin-only routes should block regular users."""
        admin = active_user(email="admin@auth.com", is_admin=True)
        user = active_user(email="user@auth.com", is_admin=False)

        # Admin can access
        with flask_app.test_request_context():
            g.current_user = admin
            assert test_client.get("/admin-only").status_code == 200

        # User is blocked
        with flask_app.test_request_context():
            g.current_user = user
            assert test_client.get("/admin-only").status_code == 403

    def test_require_roles(self, test_client, active_user, flask_app):
        """Role-restricted routes should only allow users with that role."""
        from init import db

        editor_role = Role.create(name="editor")
        db.session.commit()

        user = active_user(email="editor@auth.com")
        user.roles.append(editor_role)
        user.save()

        # Editor can access
        with flask_app.test_request_context():
            g.current_user = user
            assert test_client.get("/editor-only").status_code == 200

        # Other user blocked
        user2 = active_user(email="other@auth.com")
        with flask_app.test_request_context():
            g.current_user = user2
            assert test_client.get("/editor-only").status_code == 403

    def test_require_policy(self, test_client, active_user, auth_ext, flask_app):
        """Custom policies should handle logic-based authorization."""

        # Define policy: user can only edit their own profile
        def can_edit_user(user, **context):
            target_user_id = int(context.get("user_id"))
            return user.is_admin or user.id == target_user_id

        auth_ext.define_policy("edit_user", can_edit_user)

        user1 = active_user(email="u1@auth.com")
        user2 = active_user(email="u2@auth.com")

        # User 1 can edit User 1
        with flask_app.test_request_context():
            g.current_user = user1
            assert test_client.get(f"/user/{user1.id}/edit").status_code == 200

        # User 1 cannot edit User 2
        with flask_app.test_request_context():
            g.current_user = user1
            assert test_client.get(f"/user/{user2.id}/edit").status_code == 403

    def test_require_with_token(self, test_client, active_user):
        """Policy engine should correctly identify users from Bearer tokens."""
        admin = active_user(email="token-admin@auth.com", is_admin=True)
        token = admin.generate_api_token("test")
        from init import db

        db.session.commit()

        # Success with token (no need for g.current_user here as token_required sets it)
        response = test_client.get(
            "/api/admin", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
