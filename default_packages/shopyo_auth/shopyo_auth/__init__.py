from typing import Any
import os
import json

from flask import Flask
from .view import module_blueprint
from .upload import upload

__version__ = "1.2.0"

info = {}
with open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.json") as f:
    info = json.load(f)


default_config = {"SHOPYO_AUTH_URL": "/shopyo-auth"}


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

        app.extensions["shopyo_auth"] = self
        bp = module_blueprint
        app.register_blueprint(bp, url_prefix=app.config["SHOPYO_AUTH_URL"])
        app.jinja_env.globals["shopyo_auth"] = self

    def get_info(self):
        return info
