.. :tocdepth:: 5

Assets Management
=================

Shopyo implements a **Transparent Static Shadowing** system. This allows you to use standard Flask asset patterns while maintaining a modular file structure.

The Standard Way (Recommended)
------------------------------

You can use the standard Flask ``url_for('static', ...)`` for both global and module-specific assets.

**For a module asset:**

.. code-block:: html

   <!-- In a Jinja template -->
   <link rel="stylesheet" href="{{ url_for('static', filename='modules/auth/style.css') }}">

**For a global asset:**

.. code-block:: html

   <link rel="stylesheet" href="{{ url_for('static', filename='css/global.css') }}">

How it Works
------------

1. **Development (DEBUG=True):**
   Shopyo intercepts requests to ``/static/modules/<module_name>/...`` and dynamically serves the file directly from your module's ``static/`` folder. You don't need to run any commands to see your changes.

2. **Production (DEBUG=False):**
   You run the collection command:

   .. code-block:: bash

      shopyo collectstatic

   This physically copies all module assets into the root ``static/modules/`` directory. This allows high-performance web servers like **Nginx** to serve all assets from a single physical location without touching the Python process.

The Legacy Way
--------------

Shopyo provides a helper ``get_static``, though standard ``url_for`` is preferred in Shopyo 2.0.

.. code-block:: python

   from shopyo.api.assets import get_static

   @module_blueprint.route('/img_test')
   def img_test():
       return '<img src="{}">'.format(get_static('auth', 'logo.png'))

Summary
-------

- **Global assets:** Place in ``/static/``.
- **Module assets:** Place in ``/modules/<name>/static/``.
- **Dev mode:** Changes are instant.
- **Production:** Run ``shopyo collectstatic`` before deploying.
