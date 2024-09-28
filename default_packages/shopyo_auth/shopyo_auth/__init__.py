from typing import Any

from flask import Flask
from .view import module_blueprint

__version__ = "1.0.0"


class ShopyoAuth:
    def __init__(self, app: Any = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions["shopyo_auth"] = self
        bp = module_blueprint
        app.register_blueprint(bp)
