from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum, auto


class Permission(Enum):
    """Granular permissions for the Shopyo authorization system.

    Members:
        USER_MANAGE: Create, update, delete users.
        USER_READ: View user profiles and lists.
        ROLE_MANAGE: Create, update, delete roles.
        SETTINGS_MANAGE: Modify application settings.
        CONTENT_MANAGE: Create, update, delete content.
        CONTENT_PUBLISH: Publish or approve content.
        DASHBOARD_VIEW: Access the admin dashboard.
        ADMIN_PANEL_ACCESS: Enter the admin panel at all.
    """

    USER_MANAGE = auto()
    USER_READ = auto()
    ROLE_MANAGE = auto()
    SETTINGS_MANAGE = auto()
    CONTENT_MANAGE = auto()
    CONTENT_PUBLISH = auto()
    DASHBOARD_VIEW = auto()
    ADMIN_PANEL_ACCESS = auto()


@dataclass
class Policy:
    """A named policy with a callable check.

    Attributes:
        name: Unique policy identifier (e.g. ``"perm.CONTENT_PUBLISH"``).
        check: Callable ``(user, resource=None) -> bool``.
    """

    name: str
    check: Callable[..., bool]


class PolicyEngine:
    """Central authorization engine combining role-based and policy-based access.

    Usage::

        engine = PolicyEngine()
        engine.grant("admin", Permission.ADMIN_PANEL_ACCESS)
        engine.define("perm.CONTENT_PUBLISH", lambda u, r: u.id == r.owner_id)

        # Decorator on views
        @engine.require(Permission.ADMIN_PANEL_ACCESS)
        def dashboard(): ...

        # Programmatic check
        engine.has_permission(current_user, Permission.USER_MANAGE)
    """

    def __init__(self):
        self._policies: dict[str, Policy] = {}
        self._role_permissions: dict[str, set[Permission]] = {}

    def define(self, name: str, check: Callable[..., bool]):
        """Register a custom policy check.

        Args:
            name: Policy name (convention: ``"perm.<PERMISSION_NAME>"``).
            check: Callable ``(user, resource=None) -> bool``.
        """
        self._policies[name] = Policy(name=name, check=check)

    def grant(self, role_name: str, *permissions: Permission):
        """Assign one or more permissions to a role.

        Args:
            role_name: Name of the role (e.g. ``"admin"``, ``"editor"``).
            permissions: One or more ``Permission`` enum members.
        """
        self._role_permissions.setdefault(role_name, set()).update(permissions)

    def has_permission(
        self,
        user,
        permission: Permission,
        resource: Any = None,
    ) -> bool:
        """Check whether a user holds a given permission.

        Evaluation order:
            1. Admin users bypass all checks (transitional).
            2. Any role the user belongs to is checked for the permission.
            3. If a custom policy ``perm.<PERMISSION_NAME>`` exists, it is
               invoked with ``(user, resource)``.

        Args:
            user: Flask-Login ``User`` instance (or proxy).
            permission: The ``Permission`` enum member to check.
            resource: Optional resource object for resource-aware policies.

        Returns:
            ``True`` if the user has the permission, ``False`` otherwise.
        """
        if user.is_admin:
            return True
        for role in getattr(user, "roles", []):
            if permission in self._role_permissions.get(role.name, set()):
                return True
        policy_name = f"perm.{permission.name}"
        if policy_name in self._policies:
            return self._policies[policy_name].check(user, resource)
        return False

    def require(self, permission: Permission, resource: Any = None):
        """Decorator factory that protects routes with a permission check.

        Returns 401 if the user is unauthenticated, 403 if the user lacks
        the required permission.

        Args:
            permission: The ``Permission`` required to access the route.
            resource: Optional resource passed to the policy check.

        Example::

            @blueprint.route("/admin")
            @engine.require(Permission.ADMIN_PANEL_ACCESS)
            def admin_index():
                return "Admin panel"
        """
        from functools import wraps
        from flask import abort, g
        from flask_login import current_user

        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                user = getattr(g, "current_user", None) or current_user
                if not user.is_authenticated:
                    abort(401)
                if not self.has_permission(user, permission, resource):
                    abort(403)
                return f(*args, **kwargs)

            return wrapper

        return decorator
