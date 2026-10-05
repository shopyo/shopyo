from typing import Any
import os
import json
from flask import Flask, current_app
from shopyo_dashboard.view import module_blueprint

__version__ = "1.5.3"

info = {}
with open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.json") as f:
    info = json.load(f)

default_config = {
    "SHOPYO_DASHBOARD_URL": "/shopyo-dashboard",
    # Shown as <meta name="description"> and og/twitter description on pages
    # that do not define their own {% block description %}.
    "SHOPYO_DASHBOARD_DESCRIPTION": "Shopyo application",
    # Absolute URL used for og:image / twitter:image. Empty falls back to the
    # packaged logo (static/shopyo.png).
    "SHOPYO_DASHBOARD_OG_IMAGE": "",
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
        app.register_blueprint(
            bp, url_prefix=app.config.get("SHOPYO_DASHBOARD_URL") or bp.url_prefix
        )
        app.jinja_env.globals["shopyo_dashboard"] = self

    def get_info(self):
        info.update({"url_prefix": current_app.config["SHOPYO_DASHBOARD_URL"]})
        return info
