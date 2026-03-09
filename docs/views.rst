Views
=====

Shopyo simplifies Flask View management by using the `ModuleHelp` utility. This abstraction handles Blueprint registration, template path resolution, and metadata loading automatically.

The ModuleHelp Abstraction
**************************

When you create a new module with `shopyo startapp`, it generates a `view.py` with the following boilerplate:

.. code-block:: python

    from shopyo.api.module import ModuleHelp

    # Initializes help for the current module
    mhelp = ModuleHelp(__file__, __name__)

    # Registers the blueprint automatically based on info.json
    blueprint = mhelp.blueprint

    @blueprint.route("/")
    def index():
        return mhelp.info['display_string']

View Key Features
*****************

- **Automatic Blueprint Creation**: The blueprint name and URL prefix are pulled directly from the module's `info.json`.
- **Template Context**: `mhelp.context()` provides a dictionary with module-specific information (like `info.json` data) that you can easily update and pass to your templates.
- **Simplified Rendering**: `mhelp.render('index.html', **context)` automatically looks for templates in the module's `templates/<module_name>/` directory.

Standard Flask usage
********************

Since `module_blueprint` is just a standard Flask `Blueprint` object, you can use all standard Flask decorators and features as usual.
