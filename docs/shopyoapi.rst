Shopyo api
==========

Shopyo has some api which eases your life


api.assets
------------------

.. automodule:: shopyo.api.assets
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:


api.constants
------------------

.. automodule:: shopyo.api.constants
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:



api.database
------------------

.. automodule:: shopyo.api.database
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:


api.email
------------------

.. automodule:: shopyo.api.email
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:


api.enhance
-----------------

.. automodule:: shopyo.api.enhance
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

api.file
--------------

.. automodule:: shopyo.api.file
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:



api.forms
---------------

.. automodule:: shopyo.api.forms
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

api.html
--------------

.. automodule:: shopyo.api.html
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

api.info
--------------

.. automodule:: shopyo.api.info
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:


api.models
-----------------

.. automodule:: shopyo.api.models
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:



api.module
-----------------

.. automodule:: shopyo.api.module
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:


api.perms
-----------------

Policy-based authorization system replacing ``is_admin`` checks with a
``Permission`` + ``PolicyEngine`` approach.

**Usage:**

.. code-block:: python

    from shopyo.api.perms import PolicyEngine, Permission

    engine = PolicyEngine()

    # Grant permissions to roles
    engine.grant("admin", Permission.ADMIN_PANEL_ACCESS, Permission.USER_MANAGE)
    engine.grant("editor", Permission.CONTENT_MANAGE)

    # Define custom policy checks
    engine.define("perm.CONTENT_PUBLISH", lambda user, resource: user.id == resource.owner_id)

    # Use as a decorator on views
    @engine.require(Permission.ADMIN_PANEL_ACCESS)
    def dashboard():
        return "Admin dashboard"

    # Programmatic check
    if engine.has_permission(current_user, Permission.USER_MANAGE):
        ...

.. automodule:: shopyo.api.perms
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:


api.security
-----------------

.. automodule:: shopyo.api.security
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:


api.templates
-----------------

.. automodule:: shopyo.api.templates
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:


api.validators
-----------------

.. automodule:: shopyo.api.validators
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:



api.response
-----------------

.. automodule:: shopyo.api.response
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:


api.endpoint
-----------------

.. automodule:: shopyo.api.endpoint
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
