from typing import Any
import os
import json

from flask import Flask
from flask import current_app
from shopyo_base.view import module_blueprint

__version__ = "1.7.1"


info = {}
with open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.json") as f:
    info = json.load(f)

default_config = {
    "SHOPYO_BASE_URL": "/shopyo-base",
    "SHOPYO_BASE_NAV_LOGIN": True,
    "SHOPYO_BASE_NAV_REGISTER": True,
}


class ShopyoBase:
    def __init__(self, app: Any = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        if not hasattr(app, "extensions"):
            app.extensions = {}

        for key, value in default_config.items():
            app.config.setdefault(key, value)

        app.extensions["shopyo_base"] = self
        bp = module_blueprint
        app.register_blueprint(
            bp, url_prefix=app.config.get("SHOPYO_BASE_URL") or bp.url_prefix
        )

    def get_info(self):
        info.update({"url_prefix": current_app.config["SHOPYO_BASE_URL"]})
        return info
