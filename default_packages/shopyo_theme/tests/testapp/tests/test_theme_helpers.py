import os

import pytest


@pytest.fixture(scope="module")
def app():
    from app import create_app

    return create_app("testing")


@pytest.fixture
def client(app):
    return app.test_client()


class TestConfig:
    def test_config_values_exist(self, app):
        config = app.config
        assert "SHOPYO_THEME_URL" in config
        assert "SHOPYO_THEME_DEFAULT" in config
        assert "SHOPYO_THEME_FRONT_DEFAULT" in config
        assert "SHOPYO_THEME_BACK_DEFAULT" in config

    def test_config_values_have_expected_defaults(self, app):
        assert app.config["SHOPYO_THEME_URL"] == "/shopyo-theme"
        assert app.config["SHOPYO_THEME_FRONT_DEFAULT"] == "shopyo_theme/blogus"
        assert app.config["SHOPYO_THEME_BACK_DEFAULT"] == "shopyo_theme/mistrello"


class TestBlueprintRegistration:
    def test_blueprint_registered(self, app):
        bp = app.blueprints.get("shopyo_theme")
        assert bp is not None

    def test_blueprint_has_static_folder(self, app):
        bp = app.blueprints.get("shopyo_theme")
        assert bp is not None
        assert bp.static_folder is not None
        assert bp.static_folder.endswith("static")

    def test_blueprint_has_theme_routes(self, app):
        endpoints = [
            rule.endpoint
            for rule in app.url_map.iter_rules()
            if "shopyo_theme" in rule.endpoint
        ]
        assert "shopyo_theme.index" in endpoints
        assert "shopyo_theme.active_front_theme_css" in endpoints
        assert "shopyo_theme.active_back_theme_css" in endpoints
        assert "shopyo_theme.static" in endpoints


class TestGetBlueprintThemeDir:
    def test_plain_name_returns_none(self, app):
        with app.app_context():
            from shopyo_theme.helpers import _get_blueprint_theme_dir

            assert _get_blueprint_theme_dir("blogus") is None

    def test_unknown_blueprint_returns_none(self, app):
        with app.app_context():
            from shopyo_theme.helpers import _get_blueprint_theme_dir

            assert _get_blueprint_theme_dir("nonexistent/foo") is None

    def test_shopyo_theme_back_resolves(self, app):
        with app.app_context():
            from shopyo_theme.helpers import _get_blueprint_theme_dir

            path = _get_blueprint_theme_dir("shopyo_theme/mistrello")
            assert path is not None
            assert "static/themes/back/mistrello" in path
            assert os.path.isdir(path)

    def test_shopyo_theme_front_resolves(self, app):
        with app.app_context():
            from shopyo_theme.helpers import _get_blueprint_theme_dir

            path = _get_blueprint_theme_dir("shopyo_theme/blogus")
            assert path is not None
            assert "static/themes/front/blogus" in path
            assert os.path.isdir(path)


class TestThemeResolution:
    def test_default_front_theme(self, app):
        with app.app_context():
            from shopyo_theme.helpers import get_active_front_theme

            theme = get_active_front_theme()
            assert isinstance(theme, str)
            assert len(theme) > 0

    def test_default_back_theme(self, app):
        with app.app_context():
            from shopyo_theme.helpers import get_active_back_theme

            theme = get_active_back_theme()
            assert isinstance(theme, str)
            assert len(theme) > 0

    def test_front_theme_dir_exists(self, app):
        with app.app_context():
            from shopyo_theme.helpers import get_front_theme_dir

            d = get_front_theme_dir()
            assert os.path.isdir(d)
            assert os.path.isfile(os.path.join(d, "info.json"))

    def test_back_theme_dir_exists(self, app):
        with app.app_context():
            from shopyo_theme.helpers import get_back_theme_dir

            d = get_back_theme_dir()
            assert os.path.isdir(d)
            assert os.path.isfile(os.path.join(d, "info.json"))

    def test_front_theme_styles_url(self, app):
        with app.test_request_context():
            from shopyo_theme.helpers import get_active_front_theme_styles_url

            url = get_active_front_theme_styles_url()
            assert url.startswith("/")
            assert "styles.css" in url

    def test_back_theme_styles_url(self, app):
        with app.test_request_context():
            from shopyo_theme.helpers import get_active_back_theme_styles_url

            url = get_active_back_theme_styles_url()
            assert url.startswith("/")
            assert "styles.css" in url

    def test_front_theme_version(self, app):
        with app.app_context():
            from shopyo_theme.helpers import get_active_front_theme_version

            v = get_active_front_theme_version()
            assert isinstance(v, str)
            assert len(v) > 0

    def test_back_theme_version(self, app):
        with app.app_context():
            from shopyo_theme.helpers import get_active_back_theme_version

            v = get_active_back_theme_version()
            assert isinstance(v, str)
            assert len(v) > 0


class TestThemeCSSRoutes:
    def test_front_css_via_blueprint_static(self, app, client):
        with app.app_context():
            bp = app.blueprints.get("shopyo_theme")
            front_css = os.path.join(
                bp.static_folder, "themes", "front", "blogus", "styles.css"
            )
            assert os.path.isfile(front_css), f"Expected file at {front_css}"
        resp = client.get("/shopyo-theme/static/themes/front/blogus/styles.css")
        assert resp.status_code == 200

    def test_back_css_via_blueprint_static(self, app, client):
        with app.app_context():
            bp = app.blueprints.get("shopyo_theme")
            back_css = os.path.join(
                bp.static_folder, "themes", "back", "mistrello", "styles.css"
            )
            assert os.path.isfile(back_css), f"Expected file at {back_css}"
        resp = client.get("/shopyo-theme/static/themes/back/mistrello/styles.css")
        assert resp.status_code == 200

    def test_active_front_theme_css_endpoint(self, app, client):
        with app.test_request_context():
            from shopyo_theme.helpers import get_active_front_theme_styles_url

            url = get_active_front_theme_styles_url()
        resp = client.get(url)
        assert resp.status_code == 200

    def test_active_back_theme_css_endpoint(self, app, client):
        with app.test_request_context():
            from shopyo_theme.helpers import get_active_back_theme_styles_url

            url = get_active_back_theme_styles_url()
        resp = client.get(url)
        assert resp.status_code == 200
