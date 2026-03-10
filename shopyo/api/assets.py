import importlib
import os

from flask import current_app
from flask import send_from_directory
from flask import url_for


def get_static(boxormodule, filename):
    """
    Generates url for static file. In Shopyo 2.0, this is a thin wrapper
    around the standard Flask static handler.

    In Development (DEBUG=True): The request is intercepted by register_shopyo_static.
    In Production (DEBUG=False): The file is served from the flattened /static/modules/ folder.

    Args:
        boxormodule (String): box or module name e.g. box__default/auth or someothermodule
        filename (String): path of the file inside the box or module

    Returns
    -------
    URL for static file
    """
    # Standardize on the production-ready path
    return url_for("static", filename=f"modules/{boxormodule}/{filename}")


def register_shopyo_static(app, modules_path):
    """
    Registers a transparent interceptor for module static files in debug mode.
    This allows 'url_for('static', filename='modules/...')' to work dynamically
    during development without running collectstatic.

    Args:
        app (Flask app)
        modules_path (String): path to the modules directory
    """

    @app.route("/static/modules/<path:boxormodule>/<path:path>")
    def shopyo_static_interceptor(boxormodule, path):
        """
        Intercepts /static/modules/... and maps it to the physical module folder.
        """
        if not app.debug:
            # This should technically not be reached if called correctly,
            # but we guard for safety.
            return app.send_static_file(f"modules/{boxormodule}/{path}")

        # 1. Handle Boxed Modules (e.g., box__default/auth)
        if "box__" in boxormodule:
            # Ensure we handle various path formats (box__default/auth or auth inside a box)
            parts = boxormodule.split("/")
            if len(parts) >= 2:
                box = parts[0]
                module = parts[1]
                module_static = os.path.join(modules_path, box, module, "static")
                return send_from_directory(module_static, path=path)

        # 2. Handle Shopyo Plugins (e.g., shopyo_auth)
        if boxormodule.startswith("shopyo_"):
            try:
                plugin = importlib.import_module(boxormodule)
                # Attempt to find the static folder via the plugin's module helper
                # Fallback to standard package path discovery
                if hasattr(plugin, "view") and hasattr(plugin.view, "mhelp"):
                    plugin_folder_path = plugin.view.mhelp.dirpath
                else:
                    plugin_folder_path = os.path.dirname(plugin.__file__)

                plugin_static_folder = os.path.join(plugin_folder_path, "static")
                return send_from_directory(plugin_static_folder, path=path)
            except (ImportError, AttributeError):
                pass

        # 3. Handle Standard/Flat Modules
        module_static = os.path.join(modules_path, boxormodule, "static")
        if os.path.exists(module_static):
            return send_from_directory(module_static, path=path)

        # 4. Final Fallback: Try the actual static folder
        # (in case collectstatic was already run or it's a manual file)
        return send_from_directory(
            os.path.join(app.static_folder, "modules", boxormodule), path=path
        )


# Backward compatibility for the old name
def register_devstatic(app, modules_path):
    return register_shopyo_static(app, modules_path)
