from functools import wraps

from flask import abort
from flask import current_app
from flask import g
from flask import redirect
from flask import request
from flask import url_for
from flask_login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_email_confirmed:
            return func(*args, **kwargs)
        return redirect(url_for("shopyo_auth.unconfirmed"))

    return decorated_function


def token_required(f):
    """
    Decorator to protect API routes with Token authentication.
    Checks for Bearer token in Authorization header.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            # Fallback to session if available
            if current_user.is_authenticated:
                g.current_user = current_user
                return f(*args, **kwargs)
            return {"message": "Token is missing!"}, 401

        from .models import User

        user = User.verify_api_token(token)
        if not user:
            return {"message": "Token is invalid!"}, 401

        g.current_user = user
        return f(*args, **kwargs)

    return decorated


def roles_required(*roles):
    """
    Decorator to restrict access to users with at least one of the specified roles.
    Usage: @roles_required('admin', 'editor')
    """

    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("shopyo_auth.login"))

            user_roles = [r.name for r in current_user.roles]
            if any(role in user_roles for role in roles):
                return f(*args, **kwargs)

            return redirect("/")

        return wrap

    return decorator


def require(policy=None, roles=None, admin_only=False):
    """
    Unified authorization decorator.
    Can check for admin status, specific roles, or a custom policy.

    Usage:
    @require(admin_only=True)
    @require(roles=['admin', 'editor'])
    @require(policy='can_edit_post')
    """

    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            # Try to get user from g (set by token_required) or current_user
            user = getattr(g, "current_user", current_user)

            if not user or not user.is_authenticated:
                # If API request (has Bearer), return JSON, else redirect
                if "Authorization" in request.headers:
                    return {"message": "Authentication required"}, 401
                return redirect(url_for("shopyo_auth.login"))

            # Admin check
            if admin_only and not user.is_admin:
                abort(403)

            # Role check
            if roles:
                user_roles = [r.name for r in user.roles]
                if not any(role in user_roles for role in roles):
                    abort(403)

            # Policy check
            if policy:
                auth_ext = current_app.extensions.get("shopyo_auth")
                if not auth_ext or not auth_ext.check_policy(policy, user, **kwargs):
                    abort(403)

            return f(*args, **kwargs)

        return wrap

    return decorator
