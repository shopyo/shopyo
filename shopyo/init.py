import os

from flask_login import LoginManager
from flask_mailman import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


root_path = os.path.dirname(os.path.abspath(__file__))  # don't remove
static_path = os.path.join(root_path, "static")  # don't remove
modules_path = os.path.join(root_path, "modules")  # don't remove
themes_path = os.path.join(static_path, "themes")  # don't remove
installed_packages = []  # don't remove


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
login_manager = LoginManager()


import importlib


def load_extensions(app):
    migrate.init_app(app, db)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        for plugin in app.extensions:
            if plugin.startswith("shopyo_"):
                try:
                    module = importlib.import_module(f"{plugin}.models")
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                except Exception as e:
                    print(e)
