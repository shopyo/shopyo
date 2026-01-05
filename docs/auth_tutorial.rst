Building a Client Portal (RBAC Tutorial)
========================================

This tutorial demonstrates a real-world use case for `shopyo-auth`: creating a **Client Portal**.

**The Scenario:**
You are building a B2B application. You need a dedicated section of the site (`/portal`) that is only accessible to users with the **"client"** role. Staff members and regular users should not be able to access it.

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

       pip install shopyo-auth

Shopyo Auth Configuration
-------------------------
Enable the extension in your `app.py`. Uncomment the `shopyo_auth` lines:

.. code-block:: python

   # app.py
   from shopyo_auth import ShopyoAuth

   def create_app(config_name="development"):
       # ...
       sh_auth = ShopyoAuth()
       # ...
       sh_auth.init_app(app)
       # ...
       return app

Auth Implementation
-------------------
We will create a specific module for the client portal.

1.  **Create a Module:**
    Use the `shopyo startapp` command to create a new module named `portal`.

    .. code-block:: bash

       shopyo startapp portal

    This will create a `modules/portal` directory with the necessary files, including `view.py` and `info.json`.

2.  **Define the Restricted Route:**
    Open `modules/portal/view.py` and modify it to include the access controls.

    .. code-block:: python

       # modules/portal/view.py
       from flask import Blueprint
       from flask_login import login_required
       from shopyo_auth.decorators import roles_required
       from shopyo.api.module import ModuleHelp

              mhelp = ModuleHelp(__file__, __name__)

              blueprint = mhelp.blueprint



              @blueprint.route("/")

              @login_required

              @roles_required("client")

              def index():


           """
           Only users with the 'client' role can access this view.
           """
           return "<h1>Welcome to the Client Portal</h1><p>Restricted access area.</p>"

    *Note: The `ModuleHelp` class handles blueprint registration and `info.json` loading automatically.*

3.  **Check `info.json` (Optional):**
    Ensure `modules/portal/info.json` has the correct `url_prefix`. It typically defaults to `/{module_name}`, so it should be `/portal`.

Setting Up Roles & Users
------------------------
Now we need to create the "client" role and assign it to a user. You can do this using the Flask shell or a python script.

**Step 1: Create the Role**

.. code-block:: python

   # run: flask shell
   from shopyo_auth.models import Role
   from init import db

   client_role = Role(name="client")
   db.session.add(client_role)
   db.session.commit()
   print("Client role created!")

**Step 2: Assign Role to a User**

.. code-block:: python

   # run: flask shell
   from shopyo_auth.models import User, Role
   from init import db

   # Create a new user (or select an existing one)
   user = User()
   user.email = "client@company.com"
   user.password = "securepass"
   user.is_admin = False # They are not a superadmin

   # Add the client role
   client_role = Role.query.filter_by(name="client").first()
   user.roles.append(client_role)

   db.session.add(user)
   db.session.commit()
   print(f"User {user.email} created with 'client' role.")

Testing the Setup
-----------------
1.  Run the app: `flask run --debug`
2.  Login as `client@company.com`.
3.  Navigate to `/portal`. You should see the welcome message.
4.  Try accessing `/portal` as a different user (e.g., admin). You should be denied access (403 Forbidden).

Auth Demo Source Code
---------------------
You can view the source code for a similar setup at `shopyo/demo/auth_demo`.
