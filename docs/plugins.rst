Plugins
=======

Shopyo's power lies in its plugin-based architecture. Modules are plugins.

What is a Plugin?
-----------------

A Shopyo module is a self-contained plugin with:

* Isolated views (routes)
* Isolated models (database)
* Isolated forms
* Isolated templates
* Isolated tests

Plugins cannot directly import each other. This prevents tight coupling.

Communication Between Plugins
-----------------------------

Use the event system to communicate between modules:

.. code-block:: python

    from shopyo.api.module import get_module, dispatch

    # In one module - dispatch an event
    dispatch("user:registered", {"email": user.email})

    # In another module - listen for events
    @dispatch("user:registered")
    def send_welcome_email(email):
        # Send welcome email
        pass

Loading Order
-------------

Modules load in alphabetical order. If module B depends on module A, name module A to load first (e.g., ``box__a_core``).

Disabling Modules
-----------------

To disable a module, either:

1. Delete its folder from ``modules/``
2. Remove it from ``config.py``'s ``INSTALLED_APPS``

Installing External Plugins
---------------------------

Place external modules in ``modules/`` and run:

.. code-block:: bash

    shopyo initialise

Example: Installing a Third-Party Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Clone or download a Shopyo module
    cp -r external-module modules/

    # Register it
    shopyo initialise

    # The module is now live
