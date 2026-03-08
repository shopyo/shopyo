"""
Elite Test Infrastructure for Shopyo Auth.
Designed for maximum isolation, speed, and reliability.
"""

import pytest
from flask import Blueprint, g
from shopyo.app import create_app
from init import db
from shopyo_auth import ShopyoAuth
from shopyo_theme import ShopyoTheme
from shopyo_settings import ShopyoSettings
from shopyo_auth.models import User, Role
from shopyo_auth.decorators import require, token_required, roles_required

# Blueprint for test-specific routes to avoid late registration errors
test_routes_bp = Blueprint("test_routes", __name__)

# Roles demo routes from test_auth_roles.py
demo_blueprint = Blueprint("demo", __name__)


@demo_blueprint.route("/admin-only-demo")
@roles_required("admin")
def admin_only_demo():
    return "ok"


@demo_blueprint.route("/staff-only-demo")
@roles_required("admin", "staff")
def staff_only_demo():
    return "ok"


@test_routes_bp.route("/admin-only")
@require(admin_only=True)
def admin_route():
    return "ok"


@test_routes_bp.route("/editor-only")
@require(roles=["editor"])
def editor_route():
    return "ok"


@test_routes_bp.route("/user/<int:user_id>/edit")
@require(policy="edit_user")
def edit_user(user_id):
    return "ok"


@test_routes_bp.route("/api/admin")
@token_required
@require(admin_only=True)
def api_admin():
    return "ok"


@test_routes_bp.route("/api/test-protected")
@token_required
def api_protected():
    return {"user": g.current_user.email}


@pytest.fixture(scope="session")
def base_app():
    """
    Session-scoped application factory.
    Creates the base app and registers common extensions.
    """
    app = create_app("testing")
    app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,  # Essential for programmatic testing
            "PRESERVE_CONTEXT_ON_EXCEPTION": False,
            "EMAIL_CONFIRMATION_DISABLED": True,
        }
    )

    with app.app_context():
        # Initialize extensions only once for the session
        from shopyo_base.view import module_blueprint as base_blueprint
        from shopyo_dashboard.view import module_blueprint as dashboard_blueprint

        app.register_blueprint(base_blueprint)
        app.register_blueprint(dashboard_blueprint)

        ShopyoTheme(app)
        ShopyoSettings(app)
        # ShopyoAuth is initialized here; it handles its own blueprint registration
        ShopyoAuth(app)

        # Register test routes
        app.register_blueprint(test_routes_bp)
        app.register_blueprint(demo_blueprint)

        # Ensure all models are loaded
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope="function")
def flask_app(base_app):
    """
    Function-scoped fixture providing a clean state for each test.
    """
    with base_app.app_context():
        db.session.begin_nested()
        yield base_app
        db.session.rollback()
        # Clean up database to avoid leaks between tests
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def test_client(flask_app):
    """Clean client for functional testing."""
    return flask_app.test_client()


@pytest.fixture
def auth_ext(flask_app):
    """Access to the ShopyoAuth extension instance."""
    return flask_app.extensions["shopyo_auth"]


@pytest.fixture
def active_user(flask_app):
    """Fixture factory for creating users on demand."""

    def _create_user(
        email="test@example.com",
        password="Pass1234!@#$",
        is_admin=False,
        is_email_confirmed=True,
    ):
        user = User.create(
            email=email,
            password=password,
            is_admin=is_admin,
            is_email_confirmed=is_email_confirmed,
        )
        if is_admin:
            admin_role = Role.query.filter_by(name="admin").first()
            if not admin_role:
                admin_role = Role.create(name="admin")
            user.roles.append(admin_role)
        db.session.commit()
        return user

    return _create_user


@pytest.fixture
def auth_user(flask_app):
    """Context manager to reliably set authenticated user in 'g' for tests."""
    from contextlib import contextmanager

    @contextmanager
    def _auth(user):
        from flask import g

        with flask_app.test_request_context():
            g.current_user = user
            yield

    return _auth


@pytest.fixture
def email_config(request, flask_app):
    """
    Fixture for temporally changing configs.
    """
    config_name, config_val = request.param
    old = flask_app.config.get(config_name)

    if config_val == "remove":
        if config_name in flask_app.config:
            del flask_app.config[config_name]
    else:
        flask_app.config[config_name] = config_val

    yield
    flask_app.config[config_name] = old
