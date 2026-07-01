from typing import Any
import importlib
import os
import json
from flask import Flask
from flask import current_app
from shopyo_theme.view import module_blueprint
from .helpers import *
from shopyo.api.file import trycopytree


__version__ = "1.7.0"

info = {}
with open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.json") as f:
    info = json.load(f)

default_config = {
    "SHOPYO_THEME_URL": "/shopyo-theme",
    "SHOPYO_THEME_DEFAULT": "shopyo_theme/blogus",
    "SHOPYO_THEME_FRONT_DEFAULT": "shopyo_theme/blogus",
    "SHOPYO_THEME_BACK_DEFAULT": "shopyo_theme/mistrello",
}


def _ensure_themes(app):
    for kind in ("front", "back"):
        dest = os.path.join(app.static_folder, "themes", kind)
        if os.path.exists(dest):
            continue
        try:
            shopyo = importlib.import_module("shopyo")
            src = os.path.join(
                os.path.dirname(shopyo.__file__), "static", "themes", kind
            )
            if os.path.exists(src):
                os.makedirs(os.path.join(app.static_folder, "themes"), exist_ok=True)
                trycopytree(src, dest, verbose=False)
        except (ImportError, AttributeError):
            pass


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

        for key, value in default_config.items():
            app.config.setdefault(key, value)

        app.extensions["shopyo_theme"] = self
        bp = module_blueprint
        app.register_blueprint(bp)
        app.jinja_env.globals["shopyo_theme"] = self
        with app.app_context():
            _ensure_themes(app)

    def get_info(self):
        info.update({"url_prefix": current_app.config["SHOPYO_THEME_URL"]})
        return info
