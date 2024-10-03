from typing import Any
import os
import json
from flask import Flask
from shopyo_theme.view import module_blueprint
from .helpers import *


__version__ = "1.0.0"

info = {}
with open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.json") as f:
    info = json.load(f)


class ShopyoTheme:
    def __init__(self, app: Any = None) -> None:
        if app is not None:
            self.init_app(app)

        self.get_front_theme_dir = get_front_theme_dir
        self.get_front_theme_info_data = get_front_theme_info_data
        self.get_active_front_theme = get_active_front_theme
        self.get_active_front_theme_version = get_active_front_theme_version
        self.get_active_front_theme_styles_url = get_active_front_theme_styles_url
        self.get_back_theme_dir = get_back_theme_dir
        self.get_back_theme_info_data = get_back_theme_info_data
        self.get_active_back_theme = get_active_back_theme
        self.get_active_back_theme_version = get_active_back_theme_version
        self.get_active_back_theme_styles_url = get_active_back_theme_styles_url

    def init_app(self, app: Flask) -> None:
        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions["shopyo_theme"] = self
        bp = module_blueprint
        app.register_blueprint(bp)
        app.jinja_env.globals["shopyo_theme"] = self

    def get_info(self):
        return info
