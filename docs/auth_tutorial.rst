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
           "SHOPYO_AUTH_RATE_LIMIT": "10 per minute",
       })

       sh_auth = ShopyoAuth(app)
       return app

Rate Limiting
~~~~~~~~~~~~~

Rate limiting is **enabled by default** (``SHOPYO_AUTH_RATE_LIMIT_ENABLED`` defaults
to ``True``). Each auth endpoint has its own configurable limit:

+------------------------------------------------+------------------+----------------------------+
| Config Key                                     | Default          | Endpoint                   |
+================================================+==================+============================+
| ``SHOPYO_AUTH_RATE_LIMIT``                     | ``10 per minute``| Global fallback            |
+------------------------------------------------+------------------+----------------------------+
| ``SHOPYO_AUTH_RATE_LIMIT_LOGIN``               | ``10 per minute``| ``/shopyo-auth/login``     |
+------------------------------------------------+------------------+----------------------------+
| ``SHOPYO_AUTH_RATE_LIMIT_REGISTER``            | ``3 per minute`` | ``/shopyo-auth/register``  |
+------------------------------------------------+------------------+----------------------------+
| ``SHOPYO_AUTH_RATE_LIMIT_FORGOT_PASSWORD``     | ``3 per minute`` | ``/shopyo-auth/forgot``    |
+------------------------------------------------+------------------+----------------------------+
| ``SHOPYO_AUTH_RATE_LIMIT_RESET_PASSWORD``      | ``3 per minute`` | ``/shopyo-auth/reset``     |
+------------------------------------------------+------------------+----------------------------+

Set ``SHOPYO_AUTH_RATE_LIMIT_ENABLED = False`` to disable rate limiting entirely
(e.g., during testing).

Password Complexity
~~~~~~~~~~~~~~~~~~~

Password complexity validation is **enabled by default**
(``SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED`` defaults to ``True``).

+------------------------------------------------+----------+----------------------------------------------------+
| Config Key                                     | Default  | Description                                        |
+================================================+==========+====================================================+
| ``SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED``    | ``True`` | Enable uppercase, digit, and special-char checks   |
+------------------------------------------------+----------+----------------------------------------------------+
| ``SHOPYO_AUTH_MIN_PASSWORD_LENGTH``            | ``12``   | Minimum password length (always enforced)          |
+------------------------------------------------+----------+----------------------------------------------------+

When complexity is enabled, passwords must contain at least one:
- Uppercase letter (``A-Z``)
- Lowercase letter (``a-z``)
- Digit (``0-9``)
- Special character (e.g. ``!@#$%^&*``)

The minimum length is **always enforced** regardless of the complexity flag.
Set ``SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED = False`` to skip the character-class
rules while retaining the minimum-length check.

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

.. note::
   Tokens are hashed using **PBKDF2-HMAC-SHA256** with a per-token 32-byte
   random salt (600,000 iterations) before storage. The raw token is returned
   only once at creation time. This prevents brute-force recovery even if the
   token database is leaked.

   Previously, tokens were hashed with an unsalted ``sha256``, making them
   trivially reversible through rainbow tables. Existing tokens remain valid
   but new tokens created after the upgrade use the PBKDF2 scheme. To fully
   benefit, regenerate all existing tokens.

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
