from flask import render_template, get_template_attribute

try:
    from markupsafe import Markup
except ImportError:
    try:
        from jinja2 import Markup
    except ImportError:
        from flask import Markup


def yo_render(template, context_dict):
    """
    Renders template.

    Usage: yo_render("index.html", {"x": 1, "y": 2})
    Same as render_template("index.html", x=1, y=2)


    Args:
        template (String): template accessing
        context_dict (Dict): Template values

    Returns
    -------
    html of template
    """
    return render_template(template, **context_dict)


def yo_render_string(template_string, context_dict):
    """
    Renders a template from a string.

    Usage: yo_render_string("Hello {{ name }}!", {"name": "World"})
    """
    from flask import render_template_string

    return render_template_string(template_string, **context_dict)


def yo_get_macro(template_name, macro_name):
    """
    Gets a macro from a template for use in Python code.

    Usage:
        my_macro = yo_get_macro("macros.html", "my_macro")
        html = my_macro(arg1, arg2)
    """
    return get_template_attribute(template_name, macro_name)


def yo_safe(html_string):
    """
    Marks a string as safe for rendering (prevents auto-escaping).

    Usage: yo_safe("<b>bold</b>")
    """
    return Markup(html_string)
