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

    def get_info(self):
        info.update({"url_prefix": current_app.config["SHOPYO_AUTH_URL"]})
        return info
