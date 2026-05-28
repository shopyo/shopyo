import os
import tempfile

import pytest
from flask import Flask
from shopyo.api.assets import get_static, register_shopyo_static


def test_get_static_debug_true():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["SERVER_NAME"] = "localhost"
    register_shopyo_static(app, "/tmp/modules")
    with app.app_context():
        with app.test_request_context():
            url = get_static("box__default/auth", "style.css")
            assert "/static/modules/box__default/auth/style.css" in url


def test_get_static_debug_false():
    app = Flask(__name__)
    app.config["DEBUG"] = False
    app.config["SERVER_NAME"] = "localhost"
    with app.app_context():
        with app.test_request_context():
            url = get_static("box__default/auth", "style.css")
            assert "/static/modules/box__default/auth/style.css" in url


def test_shopyo_static_interceptor_box_module(tmp_path):
    app = Flask(__name__, static_folder=str(tmp_path / "static"))
    app.config["DEBUG"] = True
    modules_path = tmp_path / "modules"
    static_dir = tmp_path / "static" / "modules" / "box__shop" / "checkout"
    static_dir.mkdir(parents=True)
    css_file = static_dir / "style.css"
    css_file.write_text("body { color: red; }")

    register_shopyo_static(app, str(modules_path))
    client = app.test_client()

    resp = client.get("/static/modules/box__shop/checkout/style.css")
    assert resp.status_code == 200
    assert resp.data == b"body { color: red; }"


def test_shopyo_static_interceptor_flat_module(tmp_path):
    app = Flask(__name__, static_folder=str(tmp_path / "static"))
    app.config["DEBUG"] = True
    modules_path = tmp_path / "modules"
    static_dir = tmp_path / "modules" / "accounts" / "static"
    static_dir.mkdir(parents=True)
    css_file = static_dir / "app.css"
    css_file.write_text("body { background: blue; }")

    register_shopyo_static(app, str(modules_path))
    client = app.test_client()

    resp = client.get("/static/modules/accounts/app.css")
    assert resp.status_code == 200
    assert resp.data == b"body { background: blue; }"


def test_shopyo_static_interceptor_fallback(tmp_path):
    app = Flask(__name__, static_folder=str(tmp_path / "static"))
    app.config["DEBUG"] = True
    static_modules = tmp_path / "static" / "modules" / "fallback_mod"
    static_modules.mkdir(parents=True)
    css_file = static_modules / "fallback.css"
    css_file.write_text("fallback")

    register_shopyo_static(app, str(tmp_path / "modules"))
    client = app.test_client()

    resp = client.get("/static/modules/fallback_mod/fallback.css")
    assert resp.status_code == 200
    assert resp.data == b"fallback"


def test_shopyo_static_interceptor_production(tmp_path):
    app = Flask(__name__, static_folder=str(tmp_path / "static"))
    app.config["DEBUG"] = False
    static_modules = tmp_path / "static" / "modules" / "prod_mod"
    static_modules.mkdir(parents=True)
    css_file = static_modules / "prod.css"
    css_file.write_text("production")

    register_shopyo_static(app, str(tmp_path / "modules"))
    client = app.test_client()

    resp = client.get("/static/modules/prod_mod/prod.css")
    assert resp.status_code == 200
    assert resp.data == b"production"


def test_shopyo_static_plugin_with_mhelp(tmp_path):
    import shopyo

    pkg_static = os.path.join(os.path.dirname(shopyo.__file__), "static")
    os.makedirs(pkg_static, exist_ok=True)
    logo_path = os.path.join(pkg_static, "shopyo_logo.svg")
    existing = os.path.exists(logo_path)
    if not existing:
        open(logo_path, "w").close()

    try:
        app = Flask(__name__, static_folder=str(tmp_path / "static"))
        app.config["DEBUG"] = True
        register_shopyo_static(app, str(tmp_path / "modules"))
        client = app.test_client()

        resp = client.get("/static/modules/shopyo/shopyo_logo.svg")
        assert resp.status_code == 200
    finally:
        if not existing and os.path.exists(logo_path):
            try:
                os.remove(logo_path)
            except PermissionError:
                pass
        if os.path.exists(pkg_static) and not os.listdir(pkg_static):
            try:
                os.rmdir(pkg_static)
            except PermissionError:
                pass


def test_shopyo_static_plugin_import_error(tmp_path):
    app = Flask(__name__, static_folder=str(tmp_path / "static"))
    app.config["DEBUG"] = True
    modules_path = tmp_path / "modules"
    static_dir = tmp_path / "static" / "modules" / "nonexistent_pkg"
    static_dir.mkdir(parents=True)
    css_file = static_dir / "file.css"
    css_file.write_text("import-error-fallback")

    register_shopyo_static(app, str(modules_path))
    client = app.test_client()

    resp = client.get("/static/modules/nonexistent_pkg/file.css")
    assert resp.status_code == 200
    assert resp.data == b"import-error-fallback"


def test_shopyo_static_file_not_found(tmp_path):
    app = Flask(__name__, static_folder=str(tmp_path / "static"))
    app.config["DEBUG"] = True
    register_shopyo_static(app, str(tmp_path / "modules"))
    client = app.test_client()

    resp = client.get("/static/modules/unknown/ghost.css")
    assert resp.status_code == 404


def test_devstatic_alias(tmp_path):
    from shopyo.api.assets import register_devstatic

    app = Flask(__name__, static_folder=str(tmp_path / "static"))
    app.config["DEBUG"] = True
    register_devstatic(app, str(tmp_path / "modules"))
    assert True
