How to Structure a Flask App That Will Scale to 100k Users
===========================================================

.. post:: 2026-05-28
   :tags: flask, architecture, scaling, tutorial
   :category: Engineering
   :author: Shopyo Team

You started with a single ``app.py``. It felt clean. Then you added routes. Then a database. Then authentication. By the time you hit 3,000 lines, you couldn't find anything. By 10,000 lines, you were afraid to touch it.

This is the #1 problem Flask developers face — and there's almost no good documentation on how to solve it. This guide walks you through a proven architecture that scales from a weekend project to 100,000 users.

The Problem: Flask's Flexibility Is a Double-Edged Sword
---------------------------------------------------------

Flask's greatest strength — minimalism — becomes its greatest weakness as your app grows. The framework gives you blueprints and tells you "good luck." There's no enforced structure, no recommended layout for large apps, and no built-in way to organize features into isolated units.

The result? Most large Flask projects end up looking like this:

.. code-block:: text

   myapp/
   ├── app.py           # 5,000 lines
   ├── models.py        # 2,000 lines
   ├── forms.py         # 1,000 lines
   ├── helpers.py       # 800 lines
   └── templates/       # 50+ files, no structure
        ├── login.html
        ├── dashboard.html
        ├── admin.html
        └── ...

This doesn't scale. You can't find anything. Every change risks breaking something unrelated. New developers on the team spend weeks learning the undocumented structure.

The Solution: Modular Architecture
----------------------------------

Instead of organizing by *file type* (views, models, forms), organize by *feature* (auth, billing, dashboard, blog). Each feature is a self-contained module with its own views, models, forms, templates, and tests.

.. code-block:: text

   myapp/
   ├── modules/
   │   ├── auth/
   │   │   ├── view.py
   │   │   ├── models.py
   │   │   ├── forms.py
   │   │   ├── tests/
   │   │   └── templates/
   │   │       └── auth/
   │   ├── billing/
   │   │   ├── view.py
   │   │   ├── models.py
   │   │   ├── forms.py
   │   │   ├── tests/
   │   │   └── templates/
   │   │       └── billing/
   │   └── dashboard/
   │       ├── view.py
   │       ├── models.py
   │       ├── tests/
   │       └── templates/
   │           └── dashboard/
   ├── app.py
   ├── config.py
   └── requirements.txt

Each module is a Flask blueprint that registers itself. No module imports another module's internals. Communication happens through events and well-defined interfaces.

Why This Scales
---------------

1. **Isolation** — A bug in ``billing/`` can't crash ``auth/``. You can rewrite an entire module without touching the rest of the app.

2. **Discoverability** — Need to change how login works? Open ``modules/auth/view.py``. It's obvious where everything lives.

3. **Testability** — Each module has its own ``tests/`` directory. Tests are fast because they only load the module they need.

4. **Team scaling** — Five developers can work on five different modules simultaneously with zero merge conflicts.

5. **Reusability** — Need auth in your next project? Copy the ``auth/`` module. It's self-contained.

The Honest Trade-Off
--------------------

This architecture requires more upfront structure than a single ``app.py``. You need to think about module boundaries before you start coding. For a 100-line API, this is overkill. For anything that will grow beyond a few thousand lines, it's the difference between a maintainable codebase and a nightmare.

Getting Started Without the Boilerplate
---------------------------------------

Setting up this architecture manually takes about an hour. You need to:

1. Create the folder structure
2. Set up Flask blueprints for each module
3. Wire up auto-discovery so modules register themselves
4. Configure static file serving for each module
5. Set up tests for each module
6. Add authentication, an admin panel, and user management

Or you can use a framework that does all of this for you.

.. code-block:: bash

   pip install shopyo
   shopyo new myapp
   cd myapp && shopyo initialise && flask run

This gives you the architecture above — with auth, admin dashboard, auto-discovery, and scaffolding — running in 30 seconds. Every module you create with ``shopyo startapp`` follows the same structure automatically.

The key insight: **your project structure should be a feature of your framework, not a decision you make every time you start a project.** Shopyo enforces the modular architecture described in this guide so you don't have to think about it.

Further Reading
---------------

- :doc:`/usage` — Full guide to building apps with Shopyo
- :doc:`/architecture` — Deep dive into Shopyo's modular design
- :doc:`/modules` — How modules and boxes work
