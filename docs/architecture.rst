Architecture
############

If you want to understand how Shopyo actually works without wading through a sea of fluff, this is for you.

Core Philosophy
***************

Shopyo is a modular wrapper around Flask. It doesn't try to reinvent the wheel; it just gives the wheel a better axle and some decent rims. The goal is to make Flask applications modular by default, using a "Box and Module" system.

The "Box and Module" System
***************************

A Shopyo project is organized into `modules`. These modules are essentially Flask Blueprints on steroids.

- **Modules**: The basic unit of functionality. Contains its own views, models, forms, and static files.
- **Boxes**: A logical grouping of modules. Folder name must start with `box__`.

Project Structure
*****************

A typical Shopyo project looks like this:

.. code-block:: none

    /project_root
    ├── app.py          # The entry point. Defines create_app().
    ├── init.py         # The extension initializer. Defines db, login_manager, etc.
    ├── manage.py       # CLI entry point.
    └── modules/        # Where the magic (code) happens.
        ├── box__default/
        │   ├── auth/
        │   └── settings/
        └── my_custom_module/

Initialization Flow
*******************

1. **app.py**: `create_app()` is called.
2. **init.py**: `load_extensions(app)` initializes Flask extensions (SQLAlchemy, Migrate, etc.).
3. **Module Loading**: Shopyo scans the `modules/` directory.
   - It looks for `info.json` in each module to get metadata (URL prefix, etc.).
   - It registers a Blueprint for each module.
   - It imports `models.py` from each module automatically for discovery by Flask-Migrate.

Configuration
*************

Shopyo uses a profile-based configuration system defined in `config.py`. Use the `SHOPYO_CONFIG_PROFILE` environment variable to switch between `development`, `testing`, and `production`.

Static Asset Collection
***********************

To maintain modularity while serving files efficiently, Shopyo uses the `collectstatic` command. This copies static files from individual modules into a global `static/modules/` directory. Do not edit files in `static/modules/` directly; they will be overwritten.

Database Management
*******************

Shopyo wraps `Flask-Migrate`. Use `shopyo initialise` for a fresh start or standard `flask db` commands for migrations. The `shopyo clean` command is there when you inevitably mess up your local database and just want to start over.
