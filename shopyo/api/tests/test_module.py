import json
import os
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from shopyo.api.module import ModuleHelp, iter_modules


@pytest.fixture
def fake_module(tmp_path):
    module_dir = tmp_path / "modules" / "test_mod"
    module_dir.mkdir(parents=True)
    info = {"module_name": "test_mod", "url_prefix": "/test"}
    (module_dir / "info.json").write_text(json.dumps(info))
    dunder_file = module_dir / "__init__.py"
    dunder_file.touch()
    return str(dunder_file)


def test_module_help_init(fake_module):
    mh = ModuleHelp(fake_module, __name__)
    assert mh.info["module_name"] == "test_mod"
    assert mh.blueprint.name == "test_mod"
    assert mh.blueprint.url_prefix == "/test"
    assert "info" in mh._context


def test_module_help_methods(fake_module):
    mh = ModuleHelp(fake_module, __name__)
    assert mh.method("view") == "test_mod.view"
    context = mh.context()
    assert context["info"]["module_name"] == "test_mod"
    context["new"] = 1
    assert "new" not in mh._context


@patch("shopyo.api.module.get_static")
def test_get_self_static(mock_get_static, fake_module):
    mh = ModuleHelp(fake_module, __name__)
    mh.get_self_static("style.css")
    mock_get_static.assert_called_with(boxormodule="test_mod", filename="style.css")


@patch("shopyo.api.module.get_static")
def test_get_self_static_box(mock_get_static, tmp_path):
    box_dir = tmp_path / "modules" / "box__box1" / "mod1"
    box_dir.mkdir(parents=True)
    info = {"module_name": "mod1", "url_prefix": "/mod1"}
    (box_dir / "info.json").write_text(json.dumps(info))
    dunder_file = box_dir / "__init__.py"
    mh = ModuleHelp(str(dunder_file), __name__)
    mh.get_self_static("script.js")
    mock_get_static.assert_called_with(
        boxormodule="box__box1/mod1", filename="script.js"
    )


def test_render(fake_module):
    mh = ModuleHelp(fake_module, __name__)
    app = Flask(__name__)
    app.register_blueprint(mh.blueprint)
    with patch("shopyo.api.module.render_template") as mock_render:
        mh.render("index.html", var=1)
        mock_render.assert_called_with("test_mod/index.html", var=1)


def test_redirect_url(fake_module):
    mh = ModuleHelp(fake_module, __name__)
    app = Flask(__name__)
    with app.test_request_context():
        with patch("shopyo.api.module.redirect") as mock_redirect, patch(
            "shopyo.api.module.url_for"
        ) as mock_url_for:
            mh.redirect_url("test_mod.index", id=1)
            mock_url_for.assert_called_with("test_mod.index", id=1)
            mock_redirect.assert_called()


def test_iter_modules_no_modules_dir(tmp_path):
    result = list(iter_modules(str(tmp_path)))
    assert result == []


def test_iter_modules_flat(tmp_path):
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    mod_dir = modules_dir / "mymod"
    mod_dir.mkdir()
    (mod_dir / "view.py").touch()
    result = list(iter_modules(str(tmp_path)))
    assert len(result) == 1
    name, path = result[0]
    assert name == "modules.mymod"
    assert path == str(mod_dir)


def test_iter_modules_mixed(tmp_path):
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    flat_mod = modules_dir / "flatmod"
    flat_mod.mkdir()
    box_dir = modules_dir / "box__shop"
    box_dir.mkdir()
    sub_mod = box_dir / "checkout"
    sub_mod.mkdir()
    result = sorted(iter_modules(str(tmp_path)), key=lambda x: x[0])
    names = [r[0] for r in result]
    assert "modules.flatmod" in names
    assert "modules.box__shop.checkout" in names


def test_iter_modules_skips_pycache(tmp_path):
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    (modules_dir / "__pycache__").mkdir()
    (modules_dir / "my_mod").mkdir()
    result = list(iter_modules(str(tmp_path)))
    assert len(result) == 1
    assert result[0][0] == "modules.my_mod"


def test_iter_modules_box_skips_pycache_json(tmp_path):
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    box_dir = modules_dir / "box__test"
    box_dir.mkdir()
    (box_dir / "__pycache__").mkdir()
    (box_dir / "box_info.json").touch()
    (box_dir / "real_mod").mkdir()
    result = list(iter_modules(str(tmp_path)))
    assert len(result) == 1
    assert result[0][0] == "modules.box__test.real_mod"
