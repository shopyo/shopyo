from functools import wraps

from flask import redirect
from flask_login import current_user
from init import login_manager

from shopyo.api.html import notify_warning
from shopyo_auth.models import load_user as load_auth_user

# login_manager.login_message = notify_warning("Please login for access")


@login_manager.user_loader
def load_user(id):
    # delegate to shopyo_auth so the password-change session check is
    # enforced even when this module registers the loader last
    return load_auth_user(id)


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_admin:
            return f(*args, **kwargs)
        else:
            return redirect("/")

    return wrap
