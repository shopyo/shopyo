"""
Elite Tests for Role-Based Access Control (RBAC).
Verifies access restrictions based on user roles using g.current_user for reliability.
"""

import pytest
from flask import g


class TestRolesRequired:
    """Verifies that @roles_required correctly filters access."""

    def test_admin_access_allowed(self, test_client, active_user, flask_app):
        """Admin should access admin-only demo route."""
        admin = active_user(email="admin-role@auth.com", is_admin=True)
        with flask_app.test_request_context():
            g.current_user = admin
            assert test_client.get("/admin-only-demo").status_code == 200

    def test_admin_access_denied_for_non_admin(
        self, test_client, active_user, flask_app
    ):
        """Regular user should be blocked from admin-only demo route."""
        user = active_user(email="user-role@auth.com", is_admin=False)
        with flask_app.test_request_context():
            g.current_user = user
            assert test_client.get("/admin-only-demo").status_code == 403

    def test_multiple_roles_allowed(self, test_client, active_user, flask_app):
        """User with 'staff' role should access staff-only demo route."""
        from shopyo_auth.models import Role
        from init import db

        staff_role = Role.create(name="staff")
        db.session.commit()

        user = active_user(email="staff@auth.com")
        user.roles.append(staff_role)
        user.save()

        with flask_app.test_request_context():
            g.current_user = user
            assert test_client.get("/staff-only-demo").status_code == 200

    def test_unauthenticated_redirect_to_login(self, test_client):
        """Unauthenticated users should be redirected to login."""
        response = test_client.get("/admin-only-demo")
        assert response.status_code == 302
        assert "/shopyo-auth/login" in response.location
