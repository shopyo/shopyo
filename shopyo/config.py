"""
Specify main configs here

Other configs are specified in module's global.py in like
configs = {
   "development": {
       "CONFIG_VAR": "DEVVALUE"
   },
   "production": {
       "CONFIG_VAR": "PRODVALUE"
   },
   "testing": {
       "CONFIG_VAR": "TESTVALUE"
   }
}
"""

import os
import secrets
import warnings

base_path = os.path.dirname(os.path.abspath(__file__))

PRODUCTION_REQUIRED_ENV_KEYS = [
    "SECRET_KEY",
    "SQLALCHEMY_DATABASE_URI",
]

# Keys that have shipped in shopyo and are public knowledge. Never usable.
INSECURE_SECRET_KEYS = frozenset(
    {
        "",
        "secret",
        "dev-secret-key-change-in-production",
    }
)


class BaseConfig:
    """Parent configuration class."""

    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ADMIN_TEMPLATE_MODE = "bootstrap4"
    BASE_DIR = base_path
    STATIC = os.path.join(base_path, "static")
    UPLOADED_PATH_IMAGE = os.path.join(STATIC, "uploads", "images")
    UPLOADED_PATH_THUMB = os.path.join(STATIC, "uploads", "thumbs")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Canonical base URL for outbound links (e.g. password-reset
    # emails). When unset, generated links fall back to the request
    # host (or SERVER_NAME). Set it in production so emails never
    # inherit a client-supplied Host header.
    APP_URL = os.environ.get("APP_URL")

    SEED_SETTINGS = {
        "APP_NAME": "Demo",
        "ACTIVE_FRONT_THEME": "blogus",
        "ACTIVE_BACK_THEME": "boogle",
        "CURRENCY": "MUR",
    }


class ProductionConfig(BaseConfig):
    """Configurations for production"""

    # built in flask configs
    ENV = "production"
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SESSION_COOKIE_SECURE = True

    # control email confirmation for user registration
    EMAIL_CONFIRMATION_DISABLED = False

    # flask-mailman configs
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    # database configs
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

    PASSWORD_SALT = os.environ.get("PASSWORD_SALT", os.urandom(32).hex())

    def __init__(self):
        missing = [k for k in PRODUCTION_REQUIRED_ENV_KEYS if not os.environ.get(k)]
        if missing:
            raise RuntimeError(
                f"Production boot blocked: required env vars not set: {missing}"
            )
        # resolve env at instantiation time so the guard cannot be skipped by
        # passing the class around (e.g. app.config.from_object)
        self.SECRET_KEY = os.environ["SECRET_KEY"]
        self.SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
        self.PASSWORD_SALT = os.environ.get("PASSWORD_SALT") or os.urandom(32).hex()
        if self.SECRET_KEY in INSECURE_SECRET_KEYS:
            raise RuntimeError(
                "Production boot blocked: SECRET_KEY is a known default value. "
                "Generate a fresh one with `shopyo env --profile production`."
            )


class DevelopmentConfig(BaseConfig):
    """Configurations for development"""

    # built in flask configs
    ENV = "development"
    DEBUG = True
    LOGIN_DISABLED = False
    SECRET_KEY = os.environ.get("SECRET_KEY")

    def __init__(self):
        # resolve env at instantiation time so the checks cannot be skipped by
        # passing the class around (e.g. app.config.from_object)
        self.SECRET_KEY = os.environ.get("SECRET_KEY")
        self.PASSWORD_SALT = os.environ.get("PASSWORD_SALT") or secrets.token_hex(32)
        if not self.SECRET_KEY or self.SECRET_KEY in INSECURE_SECRET_KEYS:
            warnings.warn(
                "SECRET_KEY is unset or default. Set the SECRET_KEY env var "
                "(run `shopyo env` to generate a .env).",
                DeprecationWarning,
                stacklevel=2,
            )

    # control email confirmation for user registration
    EMAIL_CONFIRMATION_DISABLED = False

    # flask-mailman configs
    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = "ma@mail.com"

    # database configs
    SQLALCHEMY_DATABASE_URI = "sqlite:///shopyo.db"

    PASSWORD_SALT = os.environ.get("PASSWORD_SALT")


class TestingConfig(BaseConfig):
    """Configurations for testing"""

    # built in flask configs
    ENV = "testing"
    TESTING = True
    DEBUG = True
    SERVER_NAME = "localhost.com"
    SECRET_KEY = "secret"
    PREFERRED_URL_SCHEME = "http"
    PREFERRED_URL_SCHEME = "http"

    # flask WTF configs
    WTF_CSRF_ENABLED = False

    # control email confirmation for user registration
    EMAIL_CONFIRMATION_DISABLED = False

    # flask-mailman configs
    MAIL_BACKEND = "console"
    MAIL_USERNAME = "shopyofrom@test.com"
    MAIL_PASSWORD = "Pass1234!@#$"
    MAIL_DEFAULT_SENDER = "shopyofrom@test.com"

    # flask sqlalchemy configs
    SQLALCHEMY_DATABASE_URI = "sqlite:///testing.db"

    # flask bycrpt configs
    BCRYPT_LOG_ROUNDS = 4

    # unknown configs
    PASSWORD_SALT = "some pasword salt"
    LIVESERVER_PORT = 8943
    LIVESERVER_TIMEOUT = 10


app_config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
