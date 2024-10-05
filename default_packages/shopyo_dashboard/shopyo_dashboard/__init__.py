from typing import Any
import os
import json
from flask import Flask
from shopyo_dashboard.view import module_blueprint

__version__ = "1.1.0"

info = {}
with open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.json") as f:
    info = json.load(f)

default_config = {
    'SHOPYO_DASHBOARD_URL': '/shopyo-dashboard'
}

class ShopyoDashboard:
    def __init__(self, app: Any = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        if not hasattr(app, "extensions"):
            app.extensions = {}

        for key, value in default_config.items():
            app.config.setdefault(key, value)

        app.extensions["shopyo_dashboard"] = self
        bp = module_blueprint
        app.register_blueprint(bp, url_prefix=app.config['SHOPYO_DASHBOARD_URL'])

    def get_info(self):
        return info
