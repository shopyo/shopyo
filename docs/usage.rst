Basic Usage
===========

Shopyo requires ``Python 3.6+``. Be sure to have it before!

Installation
------------
.. tabs::

    .. group-tab:: Linux/macOS

       .. code-block:: text

          $ pip3 install shopyo

    .. group-tab:: Windows

       .. code-block:: text

          > pip install shopyo

Project Generation
------------------
Imagine you want to create your own blog usig `Flask`_. You can generate the blog project with
all project scafolding and pre-included modules such as authentication, admin, themes as follows

.. code-block:: text

    $ mkdir blog
    $ cd blog
    $ shopyo new
    $ cd blog
    $ shopyo initialise
    $ shopyo rundebug

This creates a Flask app ``blog``, initialises it and then runs it at http://localhost:5000/.
For the home page it will say ``Shopyo is now running!`` which will be the home page of your app (see
``blog/blog/modules/www/view.py`` and ``blog/static/themes/front/blogus/index.html``).
To access the dashboard, go to http://localhost:5000/auth/login and login with email
``admin@domain.com`` and password ``pass``

See :ref:`new` for more details.

.. _Flask: https://github.com/pallets/flask
