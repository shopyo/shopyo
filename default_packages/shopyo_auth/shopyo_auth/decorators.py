from functools import wraps

from flask import redirect
from flask import url_for
from flask_login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_email_confirmed:
            return func(*args, **kwargs)
        return redirect(url_for("shopyo_auth.unconfirmed"))

    return decorated_function


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
