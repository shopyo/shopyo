from flask import current_app
from flask import url_for


def get_static(boxormodule, filename):
    """
    Generates url for static file, depending on debug mode being on or not


    Args:
        boxormodule (String): box or module name e.g. box__default/auth or someothermodule/
        filename (String): path of the file inside the box or module

    Returns
    -------
    URL for static file
    """
    if current_app.config["DEBUG"] is True:
        return url_for("devstatic", boxormodule=boxormodule, path=filename)
    else:
        return url_for("static", path=f"modules/{boxormodule}/{filename}")
