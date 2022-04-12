Testing
=========

.. toctree::
    :titlesonly:


We use `pytest`_ testing framework. If running tests using pytests make sure your are inside
``shopyo/shopyo`` directory

-   To run all tests,

    .. code:: bash

        $ pytest

-   To run with more output use the verbose flag

    .. code:: bash

        $ pytest -v

-   To run tests in only a particular file or function:

    .. code:: bash

        $ pytest -k test_cli.py

Alternatively, you can run your tests via `tox`_

-   To run the complete test suit on all suported python interpretatos,
    (``python 3.6``, ``python 3.7``, ``python 3.8``, ``python 3.9``
    and test ``sphinx`` docs build):

    .. code:: bash

        $ tox

-   To run all tests only with Python 3.8 only:

    .. code:: bash

        $ tox -e py38

-   run all only the ``TestCliStartapp`` test class with Python 3.9:

    .. code:: bash

        $ tox -e py39 -- -k TestCliStartapp


To generate cov reports, install testing requirements

.. code:: bash

    $ python -m pip install -r requirements/tests.txt


Then generate the html files. They appear in shopyo/htmlcov


.. code:: bash

    $ coverage html


The use http.server to view it in the browser


.. code:: bash

    $  python -m http.server 8000 --dir htmlcov


.. _pytest: https://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes
.. _tox: https://tox.readthedocs.io/en/latest/
