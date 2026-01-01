import json
import os
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from shopyo.api.module import ModuleHelp


@pytest.fixture
def fake_module(tmp_path):
    # Create module structure
    module_dir = tmp_path / "modules" / "test_mod"
    module_dir.mkdir(parents=True)

    # Create info.json
    info = {"module_name": "test_mod", "url_prefix": "/test"}
    (module_dir / "info.json").write_text(json.dumps(info))

    # Create dunder file
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
    # Ensure it's a copy
    context["new"] = 1
    assert "new" not in mh._context


@patch("shopyo.api.module.get_static")
def test_get_self_static(mock_get_static, fake_module):
    mh = ModuleHelp(fake_module, __name__)

    # Normal module
    mh.get_self_static("style.css")
    mock_get_static.assert_called_with(boxormodule="test_mod", filename="style.css")


@patch("shopyo.api.module.get_static")
def test_get_self_static_box(mock_get_static, tmp_path):
    # Setup boxed module
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

    # We just want to check if it calls render_template with correct path
    # But since render_template requires active request context and templates,
    # we can just verify the helper method's logic if possible,
    # or mock render_template (which is imported in module.py)

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
