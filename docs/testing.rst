Testing
=======

Shopyo uses `pytest` for its test suite. Quality software requires testing; don't break the build.

Running Tests
*************

You should run tests from the project root directory.

- **Standard run**:

  .. code-block:: bash

      $ pytest

- **Verbose run**:

  .. code-block:: bash

      $ pytest -v

- **Specific test file**:

  .. code-block:: bash

      $ pytest shopyo/api/tests/test_cli.py

Continuous Integration (Tox)
****************************

We use `tox` to verify compatibility across multiple Python versions (currently supporting 3.8 up to 3.13).

- **Run all environments**:

  .. code-block:: bash

      $ tox

- **Run specific environment (e.g., Python 3.11)**:

  .. code-block:: bash

      $ tox -e py311

Coverage Reports
****************

To assess how much of the code is covered by tests, use `pytest-cov`.

1. **Install requirements**:

   .. code-block:: bash

       $ pip install -r requirements/tests.txt

2. **Generate report**:

   .. code-block:: bash

       $ pytest --cov=shopyo

3. **HTML report**:

   .. code-block:: bash

       $ pytest --cov=shopyo --cov-report=html
       $ python -m http.server 8000 --directory htmlcov
