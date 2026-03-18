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
        # 0. Handle Shopyo Plugins and core library (generic: shopyo, shopyo_auth, etc.)
        # This MUST run before app.debug check because core library assets
        # (like the logo) are not in the project's local static folder.
        try:
            pkg_name = boxormodule.split("/")[0]
            pkg = importlib.import_module(pkg_name)

            # Attempt to find the static folder via the plugin's module helper if available
            # otherwise fall back to standard package path discovery
            if hasattr(pkg, "view") and hasattr(pkg.view, "mhelp"):
                pkg_dir = pkg.view.mhelp.dirpath
            else:
                pkg_dir = os.path.dirname(pkg.__file__)

            pkg_static = os.path.join(pkg_dir, "static")
            if os.path.exists(os.path.join(pkg_static, path)):
                return send_from_directory(pkg_static, path=path)
        except (ImportError, AttributeError):
            pass

        if not app.debug:
            # Standard Flask behavior for non-library modules in production
            return app.send_static_file(f"modules/{boxormodule}/{path}")

        # 1. Handle Boxed Modules (e.g., box__default/auth)
        if "box__" in boxormodule:
            # Ensure we handle various path formats (box__default/auth or auth inside a box)
            parts = boxormodule.split("/")
            if len(parts) >= 2:
                box = parts[0]
                module = parts[1]
                module_static = os.path.join(modules_path, box, module, "static")
                if os.path.exists(module_static):
                    return send_from_directory(module_static, path=path)

        # 2. Handle Standard/Flat Modules (local to the project)
        module_static = os.path.join(modules_path, boxormodule, "static")
        if os.path.exists(module_static):
            return send_from_directory(module_static, path=path)

        # 3. Final Fallback: Try the actual static folder
        return send_from_directory(
            os.path.join(app.static_folder, "modules", boxormodule), path=path
        )


# Backward compatibility for the old name
def register_devstatic(app, modules_path):
    return register_shopyo_static(app, modules_path)
