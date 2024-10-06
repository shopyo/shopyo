from typing import Any
import os
import json
from flask import Flask
from shopyo_i18n.view import module_blueprint

# global templates variables in here
from .helpers import get_current_lang
from .helpers import get_default_lang
from .helpers import langs

__version__ = "1.1.0"

info = {}
with open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.json") as f:
    info = json.load(f)

default_config = {"SHOPYO_I18N_URL": "/shopyo-i18n"}


class Shopyoi18n:
    def __init__(self, app: Any = None) -> None:
        if app is not None:
            self.init_app(app)

        self.get_i18n_langs = langs
        self.get_default_lang = get_default_lang
        self.get_current_lang = get_current_lang

    def init_app(self, app: Flask) -> None:
        if not hasattr(app, "extensions"):
            app.extensions = {}

        for key, value in default_config.items():
            app.config.setdefault(key, value)

        app.extensions["shopyo_i18n"] = self
        bp = module_blueprint
        app.register_blueprint(bp, url_prefix=app.config["SHOPYO_I18N_URL"])
        app.jinja_env.globals["shopyo_i18n"] = self

    def get_info(self):
        return info
