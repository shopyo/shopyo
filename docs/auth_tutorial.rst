Authentication & Authorization
===============================

`shopyo-auth` is a robust authentication framework for Shopyo that provides a complete foundation for handling users, roles, and granular permissions.

Auth Key Features
-----------------

* **Granular Access Control**: Use Roles (RBAC) or complex Policies.
* **Security Hardened**: Built-in rate limiting and configurable password complexity.
* **Modern Auth**: Support for Personal Access Tokens (API Tokens).
* **Decoupled Architecture**: Hook into authentication lifecycle with Auth Events.
* **CLI Management**: Manage users and roles directly from the command line.

Auth Tutorial Prerequisites
---------------------------
1.  **Create a Project:**

    .. code-block:: bash

       mkdir my_b2b_app
       cd my_b2b_app
       shopyo new
       cd my_b2b_app
       shopyo initialise

2.  **Install Shopyo Auth:**

    .. code-block:: bash

       pip install shopyo-auth flask-limiter

Shopyo Auth Configuration
-------------------------
Enable the extension in your `app.py`. You can also configure security features:

.. code-block:: python

   # app.py
   from shopyo_auth import ShopyoAuth

   def create_app(config_name="development"):
       # ...
       app.config.update({
           "SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED": True,
           "SHOPYO_AUTH_RATE_LIMIT_ENABLED": True,
           "SHOPYO_AUTH_RATE_LIMIT": "5 per minute",
       })

       sh_auth = ShopyoAuth(app)
       return app

CLI Management
--------------
Instead of using the database shell, manage your users directly via the CLI:

**Create a User with Roles:**

.. code-block:: bash

   flask auth create-user --email client@company.com --password "Pass1234!@#$" --role client

**List Users:**

.. code-block:: bash

   flask auth list-users

**Reset Password:**

.. code-block:: bash

   flask auth reset-password client@company.com

Access Control
--------------

1. **Role-Based Access (RBAC)**
   Use the `@roles_required` decorator for simple group-based checks.

   .. code-block:: python

      from shopyo_auth.decorators import roles_required

      @blueprint.route("/portal")
      @roles_required("client")
      def portal_index():
          return "Welcome Client"

2. **Policy-Based Access (Granular)**
   Define complex logic that depends on request context (e.g., "users can only edit their own posts").

   .. code-block:: python

      # Define the policy
      def can_edit_user(user, **context):
          target_user_id = int(context.get("user_id"))
          return user.is_admin or user.id == target_user_id

      auth.define_policy("edit_user", can_edit_user)

      # Use the policy
      from shopyo_auth.decorators import require

      @blueprint.route("/user/<int:user_id>/edit")
      @require(policy="edit_user")
      def edit_user(user_id):
          return "Editing profile..."

API Tokens (Personal Access Tokens)
-----------------------------------
`shopyo-auth` allows users to generate tokens for programmatic access.

**Protecting an API route:**

.. code-block:: python

   from shopyo_auth.decorators import token_required

   @blueprint.route("/api/data")
   @token_required
   def get_data():
       from flask import g
       return {"user": g.current_user.email, "secret": "123"}

Users can manage tokens via the built-in API endpoints:
* `POST /shopyo-auth/api/tokens`: Create a token.
* `GET /shopyo-auth/api/tokens`: List tokens.
* `DELETE /shopyo-auth/api/tokens/<id>`: Revoke a token.

Auth Events System
------------------
Synchronize your application logic with authentication actions using events.

.. code-block:: python

   @auth.on("user_login")
   def log_login(user):
       print(f"User {user.email} logged in!")

   @auth.on("user_registered")
   def send_welcome(user):
       # Send custom webhook or integration
       pass

Available events: `user_registered`, `user_login`, `user_logout`, `password_reset_requested`, `password_reset_completed`.
