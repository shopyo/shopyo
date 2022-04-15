from flask import render_template


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
