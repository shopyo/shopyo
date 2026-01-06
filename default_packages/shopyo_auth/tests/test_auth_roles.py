"""
Test Role-Based Access Control
"""

import os
import sys

# Add the current directory to sys.path to make factories importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to sys.path to make demo_roles importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from flask import url_for
from shopyo_auth.models import User, Role
from factories import UserFactory, RoleFactory
from demo_roles import demo_blueprint


@pytest.mark.usefixtures("flask_app")
class TestRolesRequired:

    @pytest.fixture(autouse=True)
    def setup_demo(self, flask_app):
        flask_app.register_blueprint(demo_blueprint)

    def test_admin_access_allowed(self, test_client):
        admin_role = Role.create(name="admin")
        admin_user = UserFactory(is_email_confirmed=True)
        admin_user.roles.append(admin_role)
        admin_user.save()

        with test_client:
            # Login user
            test_client.post(
                url_for("shopyo_auth.login"),
                data={"email": admin_user.email, "password": "pass"},
                follow_redirects=True,
            )

            response = test_client.get("/admin-only")
            assert response.status_code == 200
            assert b"Welcome, Admin!" in response.data

    def test_admin_access_denied_for_non_admin(self, test_client):
        staff_role = Role.create(name="staff")
        staff_user = UserFactory(is_email_confirmed=True)
        staff_user.roles.append(staff_role)
        staff_user.save()

        with test_client:
            # Login user
            test_client.post(
                url_for("shopyo_auth.login"),
                data={"email": staff_user.email, "password": "pass"},
                follow_redirects=True,
            )

            response = test_client.get("/admin-only", follow_redirects=False)
            # Redirects to root "/"
            assert response.status_code == 302
            assert response.location == "/"

    def test_multiple_roles_allowed(self, test_client):
        staff_role = Role.create(name="staff")
        staff_user = UserFactory(is_email_confirmed=True)
        staff_user.roles.append(staff_role)
        staff_user.save()

        with test_client:
            # Login user
            test_client.post(
                url_for("shopyo_auth.login"),
                data={"email": staff_user.email, "password": "pass"},
                follow_redirects=True,
            )

            response = test_client.get("/staff-access")
            assert response.status_code == 200
            assert b"Welcome, Staff Member!" in response.data

    def test_unauthenticated_redirect_to_login(self, test_client):
        response = test_client.get("/admin-only", follow_redirects=False)
        assert response.status_code == 302
        assert "/shopyo-auth/login" in response.location
