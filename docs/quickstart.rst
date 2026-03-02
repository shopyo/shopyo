Quickstart
===========

Get a production-ready Flask app running in under 10 minutes.

---

Install Shopyo
--------------

.. code-block:: bash

    pip install shopyo

Create Your Project
-------------------

.. code-block:: bash

    # Create a new project with demo modules
    shopyo new myproject --demo

    # This automatically:
    # - Creates project structure
    # - Initializes database
    # - Creates admin user
    # - Starts development server

Or for more control:

.. code-block:: bash

    mkdir myproject
    cd myproject
    shopyo new
    shopyo env          # Generate .env file
    flask run --debug   # Start server

Access Your App
---------------

Open http://localhost:5000 in your browser.

* **Dashboard**: http://localhost:5000/dashboard
* **Login**: http://localhost:5000/auth/login
* **Credentials**: ``admin@domain.com`` / ``pass``

Create Your First Module
------------------------

.. code-block:: bash

    # Interactive mode
    shopyo startapp -i

    # Or specify directly
    shopyo startapp blog

This creates:

.. code-block:: text

    modules/
    └── blog/
        ├── __init__.py
        ├── forms.py
        ├── global.py
        ├── models.py
        ├── view.py
        ├── info.json
        ├── tests/
        │   ├── test_blog_functional.py
        │   └── test_blog_models.py
        ├── static/
        └── templates/
            └── blog/
                ├── blocks/
                │   └── sidebar.html
                ├── dashboard.html
                └── index.html

Run Initialise to Register Module
---------------------------------

.. code-block:: bash

    shopyo initialise

Your module is now live at http://localhost:5000/blog/

What's Next?
------------

* :doc:`auth_tutorial` - Add authentication to your modules
* :doc:`modules` - Understand module structure
* :doc:`architecture` - Deep dive into Shopyo's design
