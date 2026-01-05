from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mailman import Mail

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()

def load_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)