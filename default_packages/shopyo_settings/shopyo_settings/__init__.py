from typing import Any
import os
import json
from flask import Flask
from .upload import upload
from .helpers import get_setting

__version__ = "1.1.1"

info = {}
with open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.json") as f:
    info = json.load(f)


class ShopyoSettings:
    def __init__(self, app: Any = None) -> None:
        if app is not None:
            self.init_app(app)
        self.upload = upload
        self.get_setting = get_setting

    def init_app(self, app: Flask) -> None:
        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions["shopyo_settings"] = self
        app.jinja_env.globals["shopyo_settings"] = self

    def get_info(self):
        return info
