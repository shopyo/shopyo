import os
import sys
import warnings

import pytest

CONFIG_ENV_KEYS = [
    "SECRET_KEY",
    "SQLALCHEMY_DATABASE_URI",
    "PASSWORD_SALT",
]


@pytest.fixture(autouse=True)
def _clean_env():
    """Remove all config-related env vars before each test."""
    saved = {}
    for k in CONFIG_ENV_KEYS:
        saved[k] = os.environ.pop(k, None)
    # Also clear sys.modules cache so imports re-evaluate class attrs
    for mod in list(sys.modules.keys()):
        if "shopyo.config" in mod:
            del sys.modules[mod]
    yield
    for k in CONFIG_ENV_KEYS:
        if saved[k] is not None:
            os.environ[k] = saved[k]
        elif k in os.environ:
            del os.environ[k]


def _import_config():
    """Fresh import of shopyo.config with current env."""
    for mod in list(sys.modules.keys()):
        if "shopyo.config" in mod:
            del sys.modules[mod]
    import shopyo.config

    return shopyo.config


class TestProductionConfig:
    def test_missing_secret_key_raises(self):
        os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        config = _import_config()
        with pytest.raises(RuntimeError, match="SECRET_KEY"):
            config.ProductionConfig()

    def test_missing_database_uri_raises(self):
        os.environ["SECRET_KEY"] = "prod-secret"
        config = _import_config()
        with pytest.raises(RuntimeError, match="SQLALCHEMY_DATABASE_URI"):
            config.ProductionConfig()

    def test_all_env_vars_set_succeeds(self):
        os.environ["SECRET_KEY"] = "prod-secret"
        os.environ["SQLALCHEMY_DATABASE_URI"] = "postgresql:///prod"
        config = _import_config()
        cfg = config.ProductionConfig()
        assert cfg.SECRET_KEY == "prod-secret"
        assert cfg.SQLALCHEMY_DATABASE_URI == "postgresql:///prod"

    def test_session_cookie_secure(self):
        os.environ["SECRET_KEY"] = "prod-secret"
        os.environ["SQLALCHEMY_DATABASE_URI"] = "postgresql:///prod"
        config = _import_config()
        cfg = config.ProductionConfig()
        assert cfg.SESSION_COOKIE_SECURE is True

    def test_password_salt_from_env(self):
        os.environ["SECRET_KEY"] = "prod-secret"
        os.environ["SQLALCHEMY_DATABASE_URI"] = "postgresql:///prod"
        os.environ["PASSWORD_SALT"] = "explicit-salt-value"
        config = _import_config()
        cfg = config.ProductionConfig()
        assert cfg.PASSWORD_SALT == "explicit-salt-value"

    def test_password_salt_fallback_random(self):
        os.environ["SECRET_KEY"] = "prod-secret"
        os.environ["SQLALCHEMY_DATABASE_URI"] = "postgresql:///prod"
        config = _import_config()
        cfg = config.ProductionConfig()
        assert cfg.PASSWORD_SALT is not None
        assert len(cfg.PASSWORD_SALT) == 64


class TestDevelopmentConfig:
    def test_default_secret_key_warns(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = _import_config()
            config.DevelopmentConfig()
            assert any("SECRET_KEY is unset or default" in str(msg) for msg in w)

    def test_env_secret_key_no_warning(self):
        os.environ["SECRET_KEY"] = "dev-secret-from-env"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = _import_config()
            config.DevelopmentConfig()
            secret_warnings = [
                msg for msg in w if "SECRET_KEY is unset or default" in str(msg)
            ]
            assert len(secret_warnings) == 0

    def test_secret_key_from_env(self):
        os.environ["SECRET_KEY"] = "dev-secret"
        config = _import_config()
        cfg = config.DevelopmentConfig()
        assert cfg.SECRET_KEY == "dev-secret"

    def test_secret_key_default(self):
        config = _import_config()
        cfg = config.DevelopmentConfig()
        assert cfg.SECRET_KEY == "secret"

    def test_password_salt_from_env(self):
        os.environ["PASSWORD_SALT"] = "dev-salt"
        config = _import_config()
        cfg = config.DevelopmentConfig()
        assert cfg.PASSWORD_SALT == "dev-salt"

    def test_password_salt_fallback(self):
        config = _import_config()
        cfg = config.DevelopmentConfig()
        assert cfg.PASSWORD_SALT == "some pasword salt"


class TestBaseConfig:
    def test_session_cookie_defaults(self):
        config = _import_config()
        assert config.BaseConfig.SESSION_COOKIE_HTTPONLY is True
        assert config.BaseConfig.SESSION_COOKIE_SAMESITE == "Lax"
