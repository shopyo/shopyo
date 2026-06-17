Theme Development Conventions
=============================

This document covers the conventions for developing Shopyo themes,
including how bundled pip-package themes work, required template
sections, and theme resolution order.

Theme Types
-----------

Shopyo has two theme categories:

-  **Front theme** — public-facing pages (shop, blog, homepage)
-  **Back theme** — admin dashboard and internal tools

Theme Resolution
----------------

When a theme is activated, its directory is resolved in this order:

1.  **Blueprint static folder** — if the theme name is namespaced as
    ``<blueprint_name>/<theme_name>`` (e.g., ``shopyo_theme/blogus``),
    the theme is served from that blueprint's
    ``static/themes/{front|back}/`` directory.
2.  **App static folder** — otherwise, the theme is looked up in a normal
    ``static/themes/{front|back}/<theme_name>``.

For example, ``shopyo_theme/blogus`` resolves to
``shopyo_theme/static/themes/front/blogus/``, while plain ``blogus``
resolves to ``static/themes/front/blogus/``.

Package-Based Themes
--------------------

Themes bundled in pip packages are placed in the package's
``static/themes/{front|back}/<theme_name>/`` directory. The package's
blueprint must have a ``static_folder="static"`` set so that
``url_for('<blueprint>.static', filename=...)`` works.

Required File Structure
-----------------------

Every theme (front or back) must contain at least:

.. code-block:: text

    <theme_name>/
    ├── info.json              # Theme metadata
    ├── styles.css             # Main stylesheet
    ├── sections/
    │   ├── nav.html           # Navigation bar
    │   ├── footer.html        # Page footer
    │   ├── resources.html     # CSS/JS link tags
    │   └── drawer_head.html   # Mobile drawer head
    └── (other assets as needed)

info.json — Theme Metadata
---------------------------

Every theme must have an ``info.json`` at its root:

.. code-block:: json

    {
        "author": {
            "name": "Author Name",
            "website": "https://example.com",
            "mail": "author@example.com"
        },
        "version": "1.0.0",
        "display_string": "Theme Display Name"
    }

``display_string`` is shown in the admin theme picker. ``version`` is
used for cache-busting the stylesheet URL.

Required Template Sections
----------------------------

Front themes must provide these include-able templates under
``sections/``. The shop templates reference them via
``get_active_front_theme()``:

``sections/resources.html``
    Renders ``<link>`` and ``<script>`` tags. At minimum:

    .. code-block:: jinja

        <link rel="stylesheet" href="{{ get_active_front_theme_styles_url() }}">
        <link rel="stylesheet" href="/static/style.css">

``sections/nav.html``
    The top navigation bar. Typically includes login/logout links, cart
    status, and a search form.

``sections/footer.html``
    The page footer.

``sections/drawer_head.html``
    Mobile drawer/off-canvas menu head section.

Stylesheet Serving
------------------

-  For **app-based themes**, CSS is served via the
   ``active_front_theme_css`` or ``active_back_theme_css`` route.
-  For **blueprint-based themes** (namespaced), CSS is served directly
   from the blueprint's ``static_folder`` via
   ``url_for('<blueprint>.static', filename=...)``.

The ``get_active_front_theme_styles_url()`` and
``get_active_back_theme_styles_url()`` helpers handle both cases
automatically.

Example: Bundled Theme in a Package
-------------------------------------

.. code-block:: text

    my_package/
    ├── my_package/
    │   ├── __init__.py
    │   ├── view.py
    │   ├── static/
    │   │   └── themes/
    │   │       └── front/
    │   │           └── my_theme/
    │   │               ├── info.json
    │   │               ├── styles.css
    │   │               └── sections/
    │   │                   ├── nav.html
    │   │                   ├── footer.html
    │   │                   ├── resources.html
    │   │                   └── drawer_head.html
    │   └── templates/
    └── pyproject.toml

The blueprint in ``view.py`` must have ``static_folder="static"``:

.. code-block:: python

    from flask import Blueprint

    module_blueprint = Blueprint(
        "my_package",
        __name__,
        static_folder="static",    # <-- required for theme assets
        template_folder="templates",
        url_prefix="/my-package",
    )

The theme is activated by its namespaced name ``my_package/my_theme``.

``pyproject.toml`` must include the static files in package data
so they are bundled on install:

.. code-block:: toml

    [tool.setuptools]
    include-package-data = true

    [tool.setuptools.package-data]
    my_package = ["static/**", "templates/**", "**/*.json"]

Without ``static/**`` and ``**/*.json``, the theme files and metadata
will be missing from the installed package and the theme won't load.
