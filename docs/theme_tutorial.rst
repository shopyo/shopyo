Theme Tutorial
==============

Shopyo comes with a powerful built-in theming engine. This allows you to
separate the visual presentation of your application from its logic, and
switch between different designs on the fly.

This tutorial will guide you through understanding, using, and creating
themes in Shopyo.

Concepts
--------

Shopyo distinguishes between two types of themes:

1.  **Front Theme**: The theme used for the public-facing side of your
    website (e.g., landing pages, blog posts, store front).
2.  **Back Theme**: The theme used for the administration dashboard and
    internal tools.

Theme Location
--------------

Themes can live in two places:

-  **App ``static/themes/`` directory** – for project-local themes
-  **Blueprint ``static/themes/`` directory** – for themes bundled in a
   pip package (namespaced as ``<blueprint>/<theme_name>``)

Creating a Theme
----------------

Let's create a new Front theme called ``ocean_blue``.

1.  **Create the Directory**:
    Navigate to ``static/themes/front/`` and create a folder named
    ``ocean_blue``.

2.  **Add Metadata**:
    Inside ``ocean_blue``, create a file named ``info.json``.
    This file tells Shopyo about your theme.

    .. code-block:: json

        {
            "display_string": "Ocean Blue",
            "author": {
                "name": "Jane Doe",
                "website": "https://example.com",
                "mail": "jane@example.com"
            },
            "version": "1.0.0",
            "description": "A calming blue theme for the store."
        }

3.  **Add Styles**:
    Create a ``styles.css`` file in the same directory. This will be the
    main entry point for your theme's CSS.

    .. code-block:: css

        body {
            background-color: #e0f7fa;
            color: #01579b;
            font-family: sans-serif;
        }

        .navbar {
            background-color: #0277bd !important;
        }

4.  **Add Required Sections** (see :doc:`theme_conventions` for details):
    Create a ``sections/`` directory with ``nav.html``, ``footer.html``,
    ``resources.html``, and ``drawer_head.html``.

Using Themes in Templates
-------------------------

To make sure your templates load the CSS from the *currently active*
theme, use the theme helper in your base template:

For the Back Theme (Admin):

.. code-block:: html

    <link rel="stylesheet" href="{{ shopyo_theme.get_active_back_theme_styles_url() }}">

For the Front Theme (Public):

.. code-block:: html

    <link rel="stylesheet" href="{{ shopyo_theme.get_active_front_theme_styles_url() }}">

Activating a Theme
------------------

1.  Run your Shopyo application: ``flask run --debug``.
2.  Log in as an administrator.
3.  Go to the **Theme** module (typically found in the dashboard sidebar).
4.  You will see your new "Ocean Blue" theme listed under **Front Themes**.
5.  Click the **Activate** button.

The page should reload, and if your templates are set up correctly, you
will see your new blue background applied!

Advanced: Theme Assets
----------------------

If your theme needs images or JavaScript files, simply place them inside
your theme folder (e.g., ``static/themes/front/ocean_blue/assets/``).

You can reference them in your CSS relative to the CSS file:

.. code-block:: css

    .hero-banner {
        background-image: url('assets/banner.jpg');
    }

Or if you need to link to them from Jinja templates, you might need to
construct the path manually or use a helper, but typically themes are
self-contained via their CSS.
