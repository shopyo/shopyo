"""
File conftest.py for auth testing contains pytest fixtures that are only in
box__default/auth module. Refer to https://docs.pytest.org/en/stable/fixture.html
for more details on pytest
"""

import pytest
from shopyo.app import create_app
from init import db
from shopyo_auth.view import module_blueprint
from shopyo_base.view import module_blueprint as base_blueprint
from shopyo_theme import ShopyoTheme
from shopyo_settings import ShopyoSettings
from shopyo_settings.models import Settings
from shopyo_dashboard.view import module_blueprint as dashboard_blueprint


@pytest.fixture
def flask_app():
    app = create_app("testing")
    with app.app_context():
        app.register_blueprint(module_blueprint)
        app.register_blueprint(base_blueprint)
        app.register_blueprint(dashboard_blueprint)
        ShopyoTheme(app)
        ShopyoSettings(app)
        db.create_all()

        # Seed settings
        settings = [
            Settings(setting="APP_NAME", value="Demo"),
            Settings(setting="ACTIVE_FRONT_THEME", value="blogus"),
            Settings(setting="ACTIVE_BACK_THEME", value="boogle"),
            Settings(setting="CURRENCY", value="MUR"),
        ]
        db.session.add_all(settings)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_client(flask_app):
    return flask_app.test_client()


@pytest.fixture
def email_config(request, flask_app):
    """
    pytest fixture for temporally changing the email related configs
    To remove the config pass "remove" in @pytest.parameterize. For
    setting value to the config pass the actual value. See test_email.py
    for usage

    Args:
        request (pytest obj): a built in by pytest object used to read
            incoming fixture arguments
        flask_app (flask app): flask app fixture

    """
    config_name, config_val = request.param
    old = flask_app.config[config_name]

    if config_val == "remove":
        del flask_app.config[config_name]
    else:
        flask_app.config[config_name] = config_val
        print(f"\n{config_name}: {config_val}\n")

    yield
    flask_app.config[config_name] = old
