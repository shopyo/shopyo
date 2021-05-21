from flask import current_app
from flask import url_for


def get_static(boxormodule, filename):
    if current_app.config["DEBUG"] is True:
        return url_for("devstatic", boxormodule=boxormodule, filename=filename)
    else:
        return url_for("static", filename=f"modules/{boxormodule}/{filename}")
