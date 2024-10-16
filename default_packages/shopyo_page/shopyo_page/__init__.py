from typing import Any
import os
import json
from flask import Flask
from shopyo_page.view import module_blueprint
from .helpers import get_pages

__version__ = "1.2.0"

info = {}
with open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.json") as f:
    info = json.load(f)


default_config = {"SHOPYO_PAGE_URL": "/shopyo-page"}


class ShopyoPage:
    def __init__(self, app: Any = None) -> None:
        if app is not None:
            self.init_app(app)

        self.get_pages = get_pages

    def init_app(self, app: Flask) -> None:
        if not hasattr(app, "extensions"):
            app.extensions = {}

        for key, value in default_config.items():
            app.config.setdefault(key, value)

        app.extensions["shopyo_page"] = self
        bp = module_blueprint
        app.register_blueprint(bp, url_prefix=app.config["SHOPYO_PAGE_URL"])
        app.jinja_env.globals["shopyo_page"] = self

    def get_info(self):
        return info
