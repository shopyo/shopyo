from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum, auto


class Permission(Enum):
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
    name: str
    check: Callable[..., bool]


class PolicyEngine:
    def __init__(self):
        self._policies: dict[str, Policy] = {}
        self._role_permissions: dict[str, set[Permission]] = {}

    def define(self, name: str, check: Callable[..., bool]):
        self._policies[name] = Policy(name=name, check=check)

    def grant(self, role_name: str, *permissions: Permission):
        self._role_permissions.setdefault(role_name, set()).update(permissions)

    def has_permission(
        self,
        user,
        permission: Permission,
        resource: Any = None,
    ) -> bool:
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
