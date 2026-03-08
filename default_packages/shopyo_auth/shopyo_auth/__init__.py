import os
import json
from typing import Any

from flask import Flask
from flask import current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .view import module_blueprint
from .upload import upload

__version__ = "1.5.1"

limiter = Limiter(key_func=get_remote_address)

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

        if app.config.get("SHOPYO_AUTH_RATE_LIMIT_ENABLED", False):
            limiter.init_app(app)

        app.extensions["shopyo_auth"] = self
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
