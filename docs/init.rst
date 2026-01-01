The init file
=============

The `init.py` file is the heart of Shopyo's extension management and path resolution. It handles the initialization of Flask extensions and the automatic discovery of models from packages.

Core Extensions
***************

Shopyo comes pre-configured with the following extensions:

- **SQLAlchemy**: Database ORM.
- **LoginManager**: Session management.
- **Migrate**: Database migrations (Alembic wrapper).
- **Mail**: Email support.
- **CSRFProtect**: Cross-Site Request Forgery protection.

Path Resolution
***************

The file defines several critical paths used throughout the framework:

.. code-block:: python

    root_path = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(root_path, "static")
    modules_path = os.path.join(root_path, "modules")
    themes_path = os.path.join(static_path, "themes")

Extension Loading
*****************

The `load_extensions(app)` function is responsible for binding the extension objects to the Flask application instance.

Beyond standard initialization, it also performs **Automatic Model Discovery**:

.. code-block:: python

    def load_extensions(app):
        # ... standard init_app calls ...

        with app.app_context():
            for plugin in app.extensions:
                if plugin.startswith("shopyo_"):
                    # Dynamically imports models from shopyo_ packages
                    # so they are registered with SQLAlchemy/Migrate
                    importlib.import_module(f"{plugin}.models")

This ensures that any installed Shopyo packages have their database models automatically recognized by `flask db migrate`.

Installed Packages
******************

The `installed_packages` list is where you register additional Shopyo-compatible packages that are installed via pip.

.. code-block:: python

    installed_packages = ["shopyo_appadmin", "shopyo_auth"]
