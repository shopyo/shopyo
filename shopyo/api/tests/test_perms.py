import pytest
from unittest.mock import Mock
from flask import Flask, g
from werkzeug.exceptions import Unauthorized, Forbidden
from shopyo.api.perms import Permission, Policy, PolicyEngine


class TestPermission:
    def test_enum_values(self):
        assert Permission.USER_MANAGE.value is not None
        assert Permission.USER_READ.value is not None
        assert Permission.ROLE_MANAGE.value is not None
        assert Permission.SETTINGS_MANAGE.value is not None
        assert Permission.CONTENT_MANAGE.value is not None
        assert Permission.CONTENT_PUBLISH.value is not None
        assert Permission.DASHBOARD_VIEW.value is not None
        assert Permission.ADMIN_PANEL_ACCESS.value is not None

    def test_enum_members_count(self):
        assert len(Permission) == 8


class TestPolicy:
    def test_policy_dataclass(self):
        check_fn = lambda user, resource=None: True
        policy = Policy(name="test_policy", check=check_fn)
        assert policy.name == "test_policy"
        assert policy.check is check_fn


@pytest.fixture
def engine():
    return PolicyEngine()


@pytest.fixture
def app():
    return Flask(__name__)


class TestPolicyEngine:
    def test_init(self, engine):
        assert engine._policies == {}
        assert engine._role_permissions == {}

    def test_define(self, engine):
        check_fn = lambda user, resource=None: True
        engine.define("can_do_x", check_fn)
        assert "can_do_x" in engine._policies
        assert engine._policies["can_do_x"].name == "can_do_x"
        assert engine._policies["can_do_x"].check is check_fn

    def test_grant(self, engine):
        engine.grant("admin", Permission.USER_MANAGE, Permission.USER_READ)
        assert engine._role_permissions["admin"] == {
            Permission.USER_MANAGE,
            Permission.USER_READ,
        }

    def test_grant_multiple_calls(self, engine):
        engine.grant("admin", Permission.USER_MANAGE)
        engine.grant("admin", Permission.USER_READ)
        assert engine._role_permissions["admin"] == {
            Permission.USER_MANAGE,
            Permission.USER_READ,
        }

    def test_grant_different_roles(self, engine):
        engine.grant("admin", Permission.USER_MANAGE)
        engine.grant("editor", Permission.CONTENT_MANAGE)
        assert engine._role_permissions["admin"] == {Permission.USER_MANAGE}
        assert engine._role_permissions["editor"] == {Permission.CONTENT_MANAGE}

    def test_has_permission_admin_bypass(self, engine):
        user = Mock(is_admin=True, roles=[])
        assert engine.has_permission(user, Permission.ADMIN_PANEL_ACCESS)
        assert engine.has_permission(user, Permission.USER_MANAGE)
        assert engine.has_permission(user, Permission.SETTINGS_MANAGE)

    def test_has_permission_no_permission(self, engine):
        user = Mock(is_admin=False, roles=[])
        assert not engine.has_permission(user, Permission.ADMIN_PANEL_ACCESS)

    def test_has_permission_via_role(self, engine):
        engine.grant("admin", Permission.ADMIN_PANEL_ACCESS, Permission.USER_MANAGE)
        role = Mock(name="admin", spec=["name"])
        role.name = "admin"
        user = Mock(is_admin=False, roles=[role])
        assert engine.has_permission(user, Permission.ADMIN_PANEL_ACCESS)
        assert engine.has_permission(user, Permission.USER_MANAGE)
        assert not engine.has_permission(user, Permission.SETTINGS_MANAGE)

    def test_has_permission_via_policy(self, engine):
        engine.define(
            "perm.USER_MANAGE",
            lambda user, resource=None: user.id == 1,
        )
        user_allowed = Mock(is_admin=False, roles=[], id=1)
        user_denied = Mock(is_admin=False, roles=[], id=2)
        assert engine.has_permission(user_allowed, Permission.USER_MANAGE)
        assert not engine.has_permission(user_denied, Permission.USER_MANAGE)

    def test_has_permission_with_resource(self, engine):
        engine.define(
            "perm.CONTENT_MANAGE",
            lambda user, resource=None: resource is not None,
        )
        user = Mock(is_admin=False, roles=[])
        assert engine.has_permission(user, Permission.CONTENT_MANAGE, resource="doc")
        assert not engine.has_permission(user, Permission.CONTENT_MANAGE)

    def test_has_permission_role_overrides_policy(self, engine):
        engine.grant("admin", Permission.USER_MANAGE)
        engine.define("perm.USER_MANAGE", lambda user, resource=None: False)
        role = Mock(name="admin", spec=["name"])
        role.name = "admin"
        user = Mock(is_admin=False, roles=[role])
        assert engine.has_permission(user, Permission.USER_MANAGE)

    def test_has_permission_anonymous_user(self, engine):
        anon = Mock(is_admin=False, roles=[])
        assert not engine.has_permission(anon, Permission.ADMIN_PANEL_ACCESS)

    def test_has_permission_unknown_role(self, engine):
        role = Mock(name="superuser", spec=["name"])
        role.name = "superuser"
        user = Mock(is_admin=False, roles=[role])
        assert not engine.has_permission(user, Permission.USER_MANAGE)

    def test_has_permission_role_without_granted_perm(self, engine):
        engine.grant("admin", Permission.ADMIN_PANEL_ACCESS)
        role = Mock(name="admin", spec=["name"])
        role.name = "admin"
        user = Mock(is_admin=False, roles=[role])
        assert engine.has_permission(user, Permission.ADMIN_PANEL_ACCESS)
        assert not engine.has_permission(user, Permission.USER_MANAGE)


class TestPolicyEngineRequireDecorator:
    def test_require_allows_authenticated_with_permission(self, engine, app):
        engine.grant("admin", Permission.ADMIN_PANEL_ACCESS)
        role = Mock(name="admin", spec=["name"])
        role.name = "admin"

        @engine.require(Permission.ADMIN_PANEL_ACCESS)
        def some_view():
            return "success"

        user = Mock(is_admin=False, roles=[role], is_authenticated=True)
        with app.test_request_context():
            g.current_user = user
            result = some_view()
            assert result == "success"

    def test_require_blocked_no_permission(self, engine, app):
        @engine.require(Permission.ADMIN_PANEL_ACCESS)
        def some_view():
            return "success"

        user = Mock(is_admin=False, roles=[], is_authenticated=True)
        with app.test_request_context():
            g.current_user = user
            with pytest.raises(Forbidden):
                some_view()

    def test_require_unauthenticated(self, engine, app):
        @engine.require(Permission.ADMIN_PANEL_ACCESS)
        def some_view():
            return "success"

        user = Mock(is_admin=False, roles=[], is_authenticated=False)
        with app.test_request_context():
            g.current_user = user
            with pytest.raises(Unauthorized):
                some_view()

    def test_require_admin_bypass(self, engine, app):
        @engine.require(Permission.ADMIN_PANEL_ACCESS)
        def some_view():
            return "success"

        user = Mock(is_admin=True, roles=[], is_authenticated=True)
        with app.test_request_context():
            g.current_user = user
            result = some_view()
            assert result == "success"

    def test_require_admin_bypass_any_permission(self, engine, app):
        @engine.require(Permission.SETTINGS_MANAGE)
        def some_view():
            return "success"

        user = Mock(is_admin=True, roles=[], is_authenticated=True)
        with app.test_request_context():
            g.current_user = user
            result = some_view()
            assert result == "success"

    def test_require_via_role(self, engine, app):
        engine.grant("moderator", Permission.CONTENT_MANAGE)
        role = Mock(name="moderator", spec=["name"])
        role.name = "moderator"

        @engine.require(Permission.CONTENT_MANAGE)
        def some_view():
            return "success"

        user = Mock(is_admin=False, roles=[role], is_authenticated=True)
        with app.test_request_context():
            g.current_user = user
            result = some_view()
            assert result == "success"

    def test_require_via_policy(self, engine, app):
        engine.define(
            "perm.USER_MANAGE",
            lambda user, resource=None: hasattr(user, "special") and user.special,
        )

        @engine.require(Permission.USER_MANAGE)
        def some_view():
            return "success"

        allowed_user = Mock(
            is_admin=False, roles=[], is_authenticated=True, special=True
        )
        denied_user = Mock(
            is_admin=False, roles=[], is_authenticated=True, special=False
        )

        with app.test_request_context():
            g.current_user = allowed_user
            result = some_view()
            assert result == "success"

        with app.test_request_context():
            g.current_user = denied_user
            with pytest.raises(Forbidden):
                some_view()
