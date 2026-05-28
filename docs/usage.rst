Build Large Flask Apps Without Losing Your Sanity
==================================================

Shopyo is a modular Flask framework designed for maintainability, extensibility, and real-world scale.

**Why developers choose Shopyo:**

* Modular app architecture with enforced boundaries
* Built-in admin & authentication system
* Plugin-based module system
* Structured project layout that scales
* Production-ready foundations

.. code-block:: bash

    # Install
    pip install shopyo

    # Create project with demo
    shopyo new myproject --demo

That's it. Your Flask app is running at http://localhost:5000

---

The Problem: Flask Doesn't Scale Cleanly
----------------------------------------

Your Flask app starts small. Then features pile on. Suddenly:

* **Blueprint chaos** - Blueprints everywhere, no clear organization
* **Repeated auth setups** - Every project means rewriting login, registration, password reset
* **Admin reimplementation** - Building admin panels from scratch repeatedly
* **Tight coupling** - Modules importing each other directly, creating spaghetti
* **No modular enforcement** - Nothing prevents your app from becoming a monolith
* **Hard-to-reuse components** - Copy-paste between projects instead of modular code

You're not building an app. You're building technical debt.

The Solution: Modular Flask Done Right
--------------------------------------

Shopyo enforces modular boundaries so your Flask app doesn't collapse under its own weight.

**What is a Shopyo module?**

A self-contained unit with:

* ``view.py`` - HTTP handlers
* ``models.py`` - Database models
* ``forms.py`` - WTForms
* ``info.json`` - Module metadata
* ``tests/`` - Unit and functional tests
* ``static/`` - CSS, JS, images
* ``templates/`` - Jinja2 templates

Modules are isolated. They can't import each other directly. Communication happens through events.

**What is a Box?**

A box groups related modules:

.. code-block:: text

    modules/
    ├── box__ecommerce/
    │   ├── products/
    │   ├── orders/
    │   └── customers/
    └── box__blog/
        ├── posts/
        └── comments/

This structure keeps your codebase organized at any scale.

Quick Installation
------------------

Shopyo requires Python 3.8+

.. tabs::

    .. group-tab:: Linux/macOS

       .. code-block:: bash

           pip3 install shopyo

    .. group-tab:: Windows

       .. code-block:: bash

           pip install shopyo

Project Generation
------------------

The fastest way to start:

.. code-block:: bash

    shopyo new myproject --demo

This command:

1. Creates project structure
2. Copies demo modules (auth, dashboard, settings)
3. Initializes SQLite database
4. Creates admin user (admin@domain.com / Pass1234!@#$)
5. Starts development server

Manual Setup
~~~~~~~~~~~~

Want more control?

.. code-block:: bash

    mkdir blog
    cd blog
    shopyo new              # Create project
    shopyo env              # Generate .env
    shopyo initialise      # Setup database
    flask run --debug       # Start server

For the home page it will say ``Shopyo is now running!`` which will be the home page of your app (see
``blog/blog/modules/www/view.py`` and ``blog/static/themes/front/blogus/index.html``).
To access the dashboard, go to http://localhost:5000/auth/login and login with email
``admin@domain.com`` and password ``Pass1234!@#$``

See :ref:`new` for more details.

Environment Variables
---------------------

Shopyo can be configured using environment variables. This is especially useful for production deployments.

.. warning::
   The ``ProductionConfig`` **requires** ``SECRET_KEY`` and
   ``SQLALCHEMY_DATABASE_URI`` to be set via environment variables.
   If either is missing, the application will refuse to boot with a
   ``RuntimeError``. Hardcoded defaults are not allowed in production.

Essential Variables
===================

- ``SECRET_KEY`` (**required in production**): A long random string used to secure session cookies and other crypto needs.
- ``SQLALCHEMY_DATABASE_URI`` (**required in production**): The database connection URI (e.g., ``sqlite:///shopyo.db`` or ``postgresql://user:Pass1234!@#$@localhost/dbname``).
- ``PASSWORD_SALT``: Salt for token signing. Auto-generated as a random 64-char hex string if not set.

Session Security
===================

By default, Shopyo applies the following session cookie hardening flags:

- ``SESSION_COOKIE_HTTPONLY = True`` — prevents JavaScript access to the session cookie (mitigates XSS-based session theft).
- ``SESSION_COOKIE_SAMESITE = "Lax"`` — prevents the cookie from being sent in cross-site requests (mitigates CSRF).
- ``SESSION_COOKIE_SECURE = True`` — only sent over HTTPS (set in ``ProductionConfig`` only; development/testing use HTTP).

These defaults are set in ``BaseConfig`` and inherited by all environments. You can override them in your app's config:

.. code-block:: python

    class MyConfig(ProductionConfig):
        SESSION_COOKIE_SAMESITE = "Strict"  # even stricter cross-site policy

Admin Panel Security
====================

Shopyo's admin panel uses the policy engine (see :doc:`policy_tutorial`) to gate access:

- Unauthenticated users are redirected to the login page.
- Authenticated users without ``ADMIN_PANEL_ACCESS`` permission receive a ``403 Forbidden``.
- ``DefaultModelView`` classes in the admin require both ``is_authenticated`` and ``is_admin`` on the ``User`` model.

The ``DefaultModelView.is_accessible()`` method has been hardened to fix a
previously unreachable guard: the old ``not current_user.is_authenticated and
current_user.is_admin`` condition could never be true (``AnonymousUser.is_admin``
always returns ``False``), so unauthenticated users silently bypassed the check.
The fix splits the guard into a proper unauthenticated redirect followed by a
policy-based authorization check.

Email Configuration
===================

If you have email confirmation enabled, you must configure the following:

- ``MAIL_SERVER``: SMTP server address.
- ``MAIL_PORT``: SMTP server port.
- ``MAIL_USERNAME``: Username for the email server.
- ``MAIL_PASSWORD``: Password for the email server.
- ``MAIL_DEFAULT_SENDER``: Email address used as the sender.

Seeding Configuration
=====================

These variables are used during the ``shopyo initialise`` command to create the initial admin user:

- ``SHOPYO_AUTH_SEED_ADMIN_EMAIL``: Email for the seed admin user (no default — seeding is skipped if unset).
- ``SHOPYO_AUTH_SEED_ADMIN_PASSWORD``: Password for the seed admin user (no default — seeding is skipped if unset).

Why Not Plain Flask?
--------------------

+-------------------+---------------+--------------------+--------+
| Feature           | Plain Flask   | Flask + Blueprints | Shopyo |
+===================+===============+====================+========+
| Modular           |               |                    |        |
| Enforcement       | ❌            | ⚠️ Manual          | ✅     |
+-------------------+---------------+--------------------+--------+
| Plugin System     | ❌            | ❌                 | ✅     |
+-------------------+---------------+--------------------+--------+
| Built-in Auth     | ❌            | ❌                 | ✅     |
+-------------------+---------------+--------------------+--------+
| Admin UI          | ❌            | ❌                 | ✅     |
+-------------------+---------------+--------------------+--------+
| Structured        |               |                    |        |
| Scaling           | ❌            | ⚠️                 | ✅     |
+-------------------+---------------+--------------------+--------+

FAQ
---

Is Shopyo production-ready?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. Shopyo powers live applications including Maurilearn.com (eLearning platform), Linkolearn.com (Learn By links), and FlaskCon.com (Conference software).

How does Shopyo compare to Django?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shopyo gives you Django's modularity with Flask's flexibility. You get structure without the magic. Use only what you need.

Can I use Shopyo without the admin?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. Every module is optional. Delete what you don't need.

Is it compatible with Flask extensions?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Absolutely. Shopyo is Flask. All Flask extensions work.

How do modules communicate?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Modules communicate through Shopyo's event system. Import ``get_module`` from ``shopyo.api.module`` to dispatch and listen for events.

Can I deploy with Gunicorn?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. Shopyo works with any WSGI server:

.. code-block:: bash

    gunicorn "app:create_app('production')" -w 4

How does Shopyo handle migrations?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shopyo uses Flask-Migrate. Run ``flask db init`` and ``flask db migrate`` as usual.

Is it suitable for microservices?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. Each Shopyo module can be extracted into a separate service while maintaining the same development experience.

Does it enforce database structure?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No. Shopyo uses SQLAlchemy. You define your models however you want.

Can I build APIs only?
~~~~~~~~~~~~~~~~~~~~~~

Yes. Create modules without templates. Use Flask-RESTX or any API library.

.. _Flask: https://github.com/pallets/flask
