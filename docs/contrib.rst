.. :tocdepth:: 5

Contributing to Shopyo
======================

Shopyo is built using Flask but mimics Django so that you get to use plug and play modules,
to contribute, it's nice to know Flask well.

If you want to contribute, go ahead, we ❤️ it. We follow a 💯 % first-timers-friendly policy.
Feel free to join our `discord group`_ to ask if you ge stuck or would just like to char

This contribution guide has been adopted from the version used by `Flask`_.

.. _Flask: https://github.com/pallets/flask
.. _discord group: https://discord.com/invite/k37Ef6w
.. _setup:

First time setup
----------------
-   Download and install the `latest version of git`_.
-   Configure git with your `username`_ and `email`_.

    .. code-block:: text

        $ git config --global user.name 'your name'
        $ git config --global user.email 'your email'

-   Make sure you have a `GitHub account`_.
-   Fork Shopyo to your GitHub account by clicking the `Fork`_ button.
-   `Clone`_ the main repository locally.

    .. code-block:: text

        $ git clone https://github.com/shopyo/shopyo
        $ cd shopyo

-   Add your fork as a remote to push your work to. Replace
    ``{username}`` with your username. This names the remote ``fork``. The
    default Shopyo remote is ``origin``.

    .. code-block:: text

        git remote add fork https://github.com/{username}/shopyo

-   Create a virtualenv and actiave the `virtual environment`_:

    .. tabs::

       .. group-tab:: Linux/macOS

          .. code-block:: text

             $ python3 -m venv env
             $ . env/bin/activate

       .. group-tab:: Windows

          .. code-block:: text

             > py -3 -m venv env
             > env\Scripts\activate

-   Upgrade pip and setuptools:

    .. code-block:: text

        $ python -m pip install --upgrade pip setuptools

-   Install the development dependencies, then install Shopyo in editable
    mode:

    .. code-block:: text

        $ pip install -r requirements/dev.txt && pip install -e .

-   Install the `pre-commit`_ hooks:

    .. code-block:: text

        $ pre-commit install

-   Now initialize the app by running:

    .. code-block:: text

        $ cd shopyo
        $ shopyo initialise

-   Check if the shopyo app runs properly:

    .. code-block:: text

        $ shopyo rundebug

-   Go to the link http://127.0.0.1:5000/ and you should see ``SITE UNDER CONSTRUCTION``. Go to
    http://127.0.0.1:5000/auth/login and then you can access the dashboard by logging in
    with email ``admin@domain.com`` and password ``pass``

.. _latest version of git: https://git-scm.com/downloads
.. _username: https://docs.github.com/en/github/using-git/setting-your-username-in-git
.. _email: https://docs.github.com/en/github/setting-up-and-managing-your-github-user-account/setting-your-commit-email-address
.. _GitHub account: https://github.com/join
.. _Fork: https://github.com/shopyo/shopyo/fork
.. _Clone: https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#step-2-create-a-local-clone-of-your-fork
.. _pre-commit: https://pre-commit.com/
.. _virtual environment: https://docs.python.org/3/tutorial/venv.html

Pull Requests
-------------
Make sure you have setup the repo as explained in :ref:`setup` before making Pull Request (PR)

-   Create a branch for the issue you would like to work on:

    .. code-block:: bash

        $ git fetch origin
        $ git checkout -b <your-branch-name> origin/dev

    .. note::

        As a sanity check, you can run ``git branch`` to see the current branch you are on

-   Make sure to write tests for any new featues you add. To run the whole testsuite, see
    the command below. This many take a while. See `Testing <testing.html>`_ for useful
    commands such as running only the tests that you wrote for example.

    .. code-block:: bash

            $ tox

-   Using your favorite editor, make your changes, `committing as you go`_.

    .. code-block:: bash

        $ git add <filenames to commit>
        $ git commit -m "<put commit message here>"

-   Commiting files will run the `pre-commit`_ hook, which includes some style checks. In case
    the checks fail, it will not allow you to commit and mention the errors and there line numbers.
    Most of the time, the `pre-commit`_ hook will automatically fix the style errors so you will
    need to run the ``git commit`` command again. For the example below, after running ``git commit``,
    the `pre-commit`_ for ``flake8`` failed. In this case, remove the unsued import in ``shopyo/app.y``
    and commit again

    .. code-block:: bash

        $ git commit -m "test commit"
        pyupgrade................................................................Passed
        Reorder Python imports...................................................Passed
        black....................................................................Passed
        flake8...................................................................Failed
        - hook id: flake8
        - exit code: 1

        shopyo/app.py:2:1: F401 'json' imported but unused

        fix UTF-8 byte order marker..............................................Passed
        Trim Trailing Whitespace.................................................Passed
        Fix End of Files.........................................................Passed
        Check Yaml...........................................(no files to check)Skipped
        Debug Statements (Python)................................................Passed
        Check for added large files..............................................Passed

-   Push your commits to your fork on GitHub.

    .. code-block:: bash

        $ git push --set-upstream fork your-branch-name

-   `Create a pull request`_. You should see the PR link in the terminal after you succesfully push
    your commits. Link to the issue being addressed with ``fixes #123`` in the
    pull request. See `example PR`_. To create

.. _committing as you go: https://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes
.. _Create a pull request: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request
.. _example PR: https://github.com/shopyo/shopyo/pull/55


Setup Mail Dev Environment (Optional)
-------------------------------------

-   If you have Node.js, use the `maildev <https://github.com/maildev/maildev>`_ package. Install it using

    .. code-block:: bash

        $ npm install -g maildev

-   Then serve it using

    .. code-block:: bash

        $ maildev

-   Dev configs for this setup are:

    .. code-block:: python

        # shopyo/shopyo/config.py
        class DevelopmentConfig(Config):
            """Configurations for development"""

            ENV = "development"
            DEBUG = True
            LOGIN_DISABLED = False
            # control email confirmation for user registration
            EMAIL_CONFIRMATION_DISABLED = False
            # flask-mailman configs
            MAIL_SERVER = 'localhost'
            MAIL_PORT = 1025
            MAIL_USE_TLS = False
            MAIL_USE_SSL = False
            MAIL_USERNAME = '' # os.environ.get("MAIL_USERNAME")
            MAIL_PASSWORD = '' # os.environ.get("MAIL_PASSWORD")
            MAIL_DEFAULT_SENDER = 'ma@mail.com' # os.environ.get("MAIL_DEFAULT_SENDER")

-   Go to http://127.0.0.1:1080 where it serves it's web interface by default. See mails arrive in your inbox!

Contributing to package
-----------------------

-   run ``pip install -e .`` # if you did not
-   test ``shopyo <your options>``
-   If you want a system wide tests run ``python setup.py sdist`` then ``python -m pip install path/to/shopyo-x.x.x.tar.gz`` where shopyo-... is found in dist/

Maintainers notes
-----------------

* Version is found in ``shopyo/__init__.py``

.. literalinclude:: ../shopyo/__init__.py
   :language: python
   :linenos:
   :lines: 1-2

* to publish to pypi, run

.. code:: bash

    python setup.py publish

In ``__main__.py`` don't forget to update dev_requirements.txt
