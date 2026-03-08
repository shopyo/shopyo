import pytest
from flask import url_for, g
from shopyo_auth.models import User, Role
from shopyo_auth.decorators import require, token_required


def test_require_admin_only(test_client, flask_app):
    with flask_app.app_context():
        admin = User.create(
            email="admin@example.com", password="Pass1234!@#$", is_admin=True
        )
        user = User.create(
            email="user@example.com", password="Pass1234!@#$", is_admin=False
        )

        @flask_app.route("/admin-only")
        @require(admin_only=True)
        def admin_route():
            return "ok"

        # Admin can access
        with test_client.session_transaction() as sess:
            sess["_user_id"] = admin.id
        response = test_client.get("/admin-only")
        assert response.status_code == 200

        # User cannot access
        with test_client.session_transaction() as sess:
            sess["_user_id"] = user.id
        response = test_client.get("/admin-only")
        assert response.status_code == 403


def test_require_roles(test_client, flask_app):
    with flask_app.app_context():
        editor_role = Role.create(name="editor")
        user = User.create(email="editor@example.com", password="Pass1234!@#$")
        user.roles.append(editor_role)
        user.save()

        @flask_app.route("/editor-only")
        @require(roles=["editor"])
        def editor_route():
            return "ok"

        # Editor can access
        with test_client.session_transaction() as sess:
            sess["_user_id"] = user.id
        response = test_client.get("/editor-only")
        assert response.status_code == 200

        # Regular user cannot access
        user2 = User.create(email="other@example.com", password="Pass1234!@#$")
        with test_client.session_transaction() as sess:
            sess["_user_id"] = user2.id
        response = test_client.get("/editor-only")
        assert response.status_code == 403


def test_require_policy(test_client, flask_app):
    from shopyo_auth import ShopyoAuth

    auth = flask_app.extensions["shopyo_auth"]

    # Define a policy: user can only edit their own profile
    def can_edit_user(user, **context):
        target_user_id = int(context.get("user_id"))
        return user.is_admin or user.id == target_user_id

    auth.define_policy("edit_user", can_edit_user)

    @flask_app.route("/user/<int:user_id>/edit")
    @require(policy="edit_user")
    def edit_user(user_id):
        return "ok"

    with flask_app.app_context():
        user1 = User.create(email="u1@example.com", password="Pass1234!@#$")
        user2 = User.create(email="u2@example.com", password="Pass1234!@#$")

        # User 1 can edit User 1
        with test_client.session_transaction() as sess:
            sess["_user_id"] = user1.id
        response = test_client.get(f"/user/{user1.id}/edit")
        assert response.status_code == 200

        # User 1 cannot edit User 2
        response = test_client.get(f"/user/{user2.id}/edit")
        assert response.status_code == 403


def test_require_with_token(test_client, flask_app):
    with flask_app.app_context():
        user = User.create(
            email="token-policy@example.com", password="Pass1234!@#$", is_admin=True
        )
        token = user.generate_api_token("test")

        @flask_app.route("/api/admin")
        @token_required
        @require(admin_only=True)
        def api_admin():
            return "ok"

        # Success with token
        response = test_client.get(
            "/api/admin", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
