.. :tocdepth:: 5

Documentation
=============

``Sphinx`` is included in ``requirements/dev.txt``. Make sure to install it before
running these command as explained in :ref:`Contributing to Shopyo`
(i.e ``pip install -r requirements/dev.txt``)


-   To build the docs from source folder ``docs`` to destination folder ``docs/_build``, run

    .. code:: text

        $ sphinx-build -b html -E docs docs/_build

-   You can also build the docs by using the Sphinx Makefile as follows

    .. code:: text

        $ cd docs
        $ make html

-   To view the docs, open ``docs/_build/html/index.html`` in your browser

-   If you want the doc to auto build upon changes, use the ``sphinx-autobuild`` command intead:

    .. code:: text

        $ sphinx-autobuild docs docs/_build
