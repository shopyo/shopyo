import importlib
import os

from flask import current_app
from flask import send_from_directory
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


def register_devstatic(app, modules_path):
    """
    Resgisters endpoint for serving files in debug mode


    Args:
        app (Flask app)

    Returns
    -------
    URL for static file in debug mode
    """

    @app.route("/devstatic/<path:boxormodule>/f/<path:path>")
    def devstatic(boxormodule, path):
        if app.config["DEBUG"]:
            if boxormodule.startswith("box__"):
                box = boxormodule.split("/")[0]
                module = boxormodule.split("/")[1]
                module_static = os.path.join(modules_path, box, module, "static")
                return send_from_directory(module_static, path=path)
            if boxormodule.startswith("shopyo_"):
                plugin = importlib.import_module(boxormodule)
                plugin_folder_path = plugin.view.mhelp.dirpath
                plugin_static_folder = os.path.join(plugin_folder_path, "static")
                return send_from_directory(plugin_static_folder, path=path)
            else:
                module = boxormodule
                module_static = os.path.join(modules_path, module, "static")
                return send_from_directory(module_static, path=path)
