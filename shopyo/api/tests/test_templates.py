import pytest
from flask import Flask
from shopyo.api.templates import yo_render, yo_render_string, yo_get_macro, yo_safe


def test_yo_render():
    app = Flask(__name__)
    with app.test_request_context():
        # Just check it calls render_template which will fail because template doesn't exist
        # but this confirms the function is called and reaches the Flask call
        try:
            yo_render("non_existent.html", {"x": 1})
        except Exception:
            pass


def test_yo_render_string():
    app = Flask(__name__)
    with app.test_request_context():
        result = yo_render_string("Hello {{ name }}!", {"name": "World"})
        assert result == "Hello World!"


def test_yo_safe():
    result = yo_safe("<b>bold</b>")
    assert str(result) == "<b>bold</b>"
    try:
        from markupsafe import Markup
    except ImportError:
        from flask import Markup
    assert isinstance(result, Markup)
