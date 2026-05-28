import pytest
from flask import Flask
from shopyo.api.templates import yo_render, yo_render_string, yo_get_macro, yo_safe


def test_yo_render():
    app = Flask(__name__)
    with app.test_request_context():
        try:
            yo_render("non_existent.html", {"x": 1})
        except Exception:
            pass


def test_yo_render_string():
    app = Flask(__name__)
    with app.test_request_context():
        result = yo_render_string("Hello {{ name }}!", {"name": "World"})
        assert result == "Hello World!"


def test_yo_get_macro(tmp_path):
    app = Flask(__name__)
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    macro_file = template_dir / "macros.html"
    macro_file.write_text(
        "{% macro greet(name) %}<h1>Hello {{ name }}</h1>{% endmacro %}"
    )
    app.jinja_loader.searchpath.insert(0, str(template_dir))

    with app.app_context():
        macro = yo_get_macro("macros.html", "greet")
        result = macro("World")
        assert "<h1>Hello World</h1>" in result


def test_yo_get_macro_not_found(tmp_path):
    app = Flask(__name__)
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    app.jinja_loader.searchpath.insert(0, str(template_dir))

    with app.app_context():
        with pytest.raises(Exception):
            yo_get_macro("nonexistent.html", "greet")


def test_yo_safe():
    result = yo_safe("<b>bold</b>")
    assert str(result) == "<b>bold</b>"
    try:
        from markupsafe import Markup
    except ImportError:
        from flask import Markup
    assert isinstance(result, Markup)
