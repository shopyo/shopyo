import os
import json
from typing import Any

import click
from flask import Flask
from flask import current_app
from flask.cli import with_appcontext
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

__version__ = "1.10.0"

limiter = Limiter(key_func=get_remote_address)


@click.group("auth")
def auth_cli():
    """Shopyo Auth management commands."""
    pass


@auth_cli.command("create-user")
@click.option("--email", prompt=True, help="User email")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--admin", is_flag=True, help="Make user an admin")
@click.option("--role", multiple=True, help="Add role(s) to user")
@with_appcontext
def create_user(email, password, admin, role):
    """Create a new user."""
    from .models import User, Role

    if User.get_by_email(email):
        click.secho(f"Error: User with email {email} already exists.", fg="red")
        return

    user = User.create(email=email, password=password, is_admin=admin)
    for r_name in role:
        r = Role.query.filter_by(name=r_name).first()
        if not r:
            r = Role.create(name=r_name)
        user.roles.append(r)
    user.save()
    click.secho(f"User {email} created successfully.", fg="green")


@auth_cli.command("list-users")
@with_appcontext
def list_users():
    """List all users."""
    from .models import User

    users = User.query.all()
    click.echo(f"{'ID':<5} {'Email':<30} {'Admin':<10} {'Roles'}")
    click.echo("-" * 60)
    for user in users:
        roles = ", ".join([r.name for r in user.roles])
        click.echo(f"{user.id:<5} {user.email:<30} {str(user.is_admin):<10} {roles}")


@auth_cli.command("reset-password")
@click.argument("email")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@with_appcontext
def reset_password(email, password):
    """Reset a user's password."""
    from .models import User

    user = User.get_by_email(email)
    if not user:
        click.secho(f"Error: User {email} not found.", fg="red")
        return

    user.password = password
    user.save()
    click.secho(f"Password for {email} reset successfully.", fg="green")


from .view import module_blueprint
from .upload import upload

info = {}
with open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.json") as f:
    info = json.load(f)


default_config = {
    "SHOPYO_AUTH_URL": "/shopyo-auth",
    "SHOPYO_AUTH_REGISTER": True,
    "SHOPYO_AUTH_LOGIN_FORGET_PASSWORD": True,
    "SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED": False,
    "SHOPYO_AUTH_RATE_LIMIT_ENABLED": False,
    "SHOPYO_AUTH_RATE_LIMIT": "5 per minute",
    "SHOPYO_AUTH_SEED_ADMIN_EMAIL": os.environ.get(
        "SHOPYO_AUTH_SEED_ADMIN_EMAIL", "admin@admin.com"
    ),
    "SHOPYO_AUTH_SEED_ADMIN_PASSWORD": os.environ.get(
        "SHOPYO_AUTH_SEED_ADMIN_PASSWORD", "pass"
    ),
}


class ShopyoAuth:
    def __init__(self, app: Any = None) -> None:
        self.policies = {}
        self.events = {
            "user_registered": [],
            "user_login": [],
            "user_logout": [],
            "password_reset_requested": [],
            "password_reset_completed": [],
        }
        if app is not None:
            self.init_app(app)
        self.upload = upload

    def init_app(self, app: Flask) -> None:
        if not hasattr(app, "extensions"):
            app.extensions = {}

        for key, value in default_config.items():
            app.config.setdefault(key, value)

        # Always init, but it will only throttle if enabled via config
        limiter.init_app(app)
        # Enable/Disable based on config
        limiter.enabled = app.config.get("SHOPYO_AUTH_RATE_LIMIT_ENABLED", False)

        app.extensions["shopyo_auth"] = self
        app.cli.add_command(auth_cli)
        bp = module_blueprint
        app.register_blueprint(bp, url_prefix=app.config["SHOPYO_AUTH_URL"])
        app.jinja_env.globals["shopyo_auth"] = self

    def define_policy(self, name, func):
        """
        Defines a security policy.
        func should take (user, **context) and return bool.
        """
        self.policies[name] = func

    def check_policy(self, name, user, **context):
        if name not in self.policies:
            return False
        return self.policies[name](user, **context)

    def on(self, event_name):
        """
        Decorator to register a callback for an event.
        Usage:
        @auth.on("user_registered")
        def my_callback(user):
            ...
        """

        def decorator(func):
            if event_name not in self.events:
                self.events[event_name] = []
            self.events[event_name].append(func)
            return func

        return decorator

    def trigger(self, event_name, *args, **kwargs):
        """Triggers an event and calls all registered callbacks."""
        if event_name in self.events:
            for callback in self.events[event_name]:
                callback(*args, **kwargs)

    def get_info(self):
        info.update({"url_prefix": current_app.config["SHOPYO_AUTH_URL"]})
        return info
