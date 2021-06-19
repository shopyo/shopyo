.. :tocdepth:: 5

Contributing to Shopyo
======================

Shopyo is built using Flask but mimics Django so that you get to use plug and play modules,
to contribute, it's nice to know Flask well.

If you want to contribute, go ahead, we ❤️ it. We follow a 💯 % first-timers-friendly policy.

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
    ``{username}`` with your username. This names the remote "fork", the
    default Shopyo remote is "origin".

    .. code-block:: text

        git remote add fork https://github.com/{username}/shopyo

-   Create a virtualenv.

    .. tabs::

       .. group-tab:: Linux/macOS

          .. code-block:: text

             $ python3 -m venv env
             $ . env/bin/activate

       .. group-tab:: Windows

          .. code-block:: text

             > py -3 -m venv env
             > env\Scripts\activate

-   Upgrade pip and setuptools.

    .. code-block:: text

        $ python -m pip install --upgrade pip setuptools

-   Install the development dependencies, then install Shopyo in editable
    mode.

    .. code-block:: text

        $ pip install -r requirements/dev.txt && pip install -e .

-   Install the `pre-commit`_ hooks.

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


Start coding
------------
Make sure you have setup the repo as explained in :ref:`setup` before making Pull Request (PR)

#. Let say you are excited about a feature you want to work on. You need to first create a separate branch and work on that branch. To check which branch you are currently on run ``git branch``. Most likely you will see ``dev`` branch colored green or marked to tell you that you are on ``dev`` branch. Before creating a new branch from ``dev`` make sure you have fetched latest changes as mentioned in :ref:`setup` step 10
#. To create a branch and switch to that branch you run:

   .. code-block:: bash

      git checkout -b <name of branch>
      # example: git checkout -b add-form-validation

   .. note::
       You can do the above using 2 separate commands if that makes it easier:

       .. code-block:: bash

          # First create a new branch from current branch
          git branch <name of branch>

          # Next switch to this new branch
          git checkout <name of branch to switch to>

#. After git checkout command above, run ``git branch`` to make sure you are not working on ``dev`` branch but are on the newly created branch.
#. Now you can start working on the feature for which you want to make PR
#. Add tests for any new features that you add.
#. Run the following to make sure all the existing and new tests pass. Check the `Testing <testing.html>`_ section for more details

   .. code-block:: bash

      python -m pytest .

#. [*Optional Step*] Make sure to bump the version number in file ``shopyo/__init__.py`` as follows:
    * small fixes: ``_._.x``, (example ``3.4.6`` to ``3.4.7``)
    * feature, many fixes etc: ``_.x.0``, (example ``3.4.6`` to ``3.5.0``)
    * big feature, breaking change etc ``x.0.0`` (example ``3.4.6`` to ``4.0.0``)

#. Check that there are no linting errors according to ``flake8``. To do so you can run

   .. code-block:: bash

      flake8 <path of file that you want to check>

      # example to check the linting error for test_dashboard.py file
      # assuming you are in shopyo/shopyo directory, run
      flake8 ./modules/box__default/dashboard/tests/test_dashboard.py

   .. note::
      If the command above returns without any output, then there are no
      linting errors, otherwise it will tell you the line number and type
      of linting error.
      If typing ``flake8`` gives error related to command not found, then you
      do not have ``flake8`` installed and it can be installed as follows:

      .. code-block:: bash

         python -m pip install flake8

      In addition, if you are using `VS Code <https://code.visualstudio.com/>`__
      then you can create a ``.vscode`` folder at the root level and add ``settings.json``
      file to it with the following content. This way it auto detects the
      linting errors for you

      .. code-block:: json

         {
            "python.linting.flake8Enabled": true
         }

      If you have already created the ``settings.json`` file as mentioned in :ref:`setup` step 5,
      then your json file will look similar to one below

      For Windows OS:

      .. code-block:: json

         {
            "python.pythonPath": "${workspaceFolder}/env/Scripts/python.exe",
            "python.linting.flake8Enabled": true
         }

      For Unix/MacOS

      .. code-block:: json

         {
            "python.pythonPath": "${workspaceFolder}/env/bin/python",
            "python.linting.flake8Enabled": true
         }

#. Once you are happy with the changes you made you can double check the changed files by running:

   .. code-block:: bash

      git status

#. Next add the changes as required

   .. code-block:: bash

       git add . # to add all changes
       git add <file1 name> <file2 name> # to only add desired files

#. Commit the changes. For the commit messages, follow the guidelines `here <https://udacity.github.io/git-styleguide/>`__

   .. code-block:: bash

      git commit -m "<put your commit message here>"

#. Finally push the committed changes from local repository to a remote repository (the one you forked)

   .. code-block:: bash

      git push origin <the current branch name>

#. You can now make a PR. When you go to your forked repo or the owner's repo you will see a ``compare & pull request`` button. Click on it and mention the changes you made. Look at the `past PRs <https://github.com/Abdur-rahmaanJ/shopyo/pulls?q=is%3Apr+is%3Aclosed>`_ for examples of what to mention when submitting a PR. If a PR closes an issue, add ``Fixes #<issue number>``, as seen `here <https://github.com/Abdur-rahmaanJ/shopyo/pull/95>`_
#. [*Optional Step*] If you want you can request reviews when submitting PR.
#. [*Optional Step*] Add your country flag in readme after accepted PR.

.. note::
   At times when you do git status after fetching the latest changes it might say something like: ``Your branch is ahead of 'origin/dev`` which mean that your forked branch does not have the latest local changes and does not match the owner's repo. To push the latest changes to your forked repo, run:

   .. code-block:: bash

      git push origin head


Setup Mail Dev Environment (Optional)
-------------------------------------

If you have Node.js, use the `maildev <https://github.com/maildev/maildev>`_ package. Install it using


   .. code-block:: bash

      npm install -g maildev


Then serve it using


   .. code-block:: bash

      maildev


Dev configs for this setup:

   .. code-block:: python

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

Go to http://127.0.0.1:1080 where it serves it's web interface by default. See mails arrive in your inbox!

Contributing to package
-----------------------

* run ``pip install -e .`` # if you did not
* test ``shopyo <your options>``

If you want a system wide tests run ``python setup.py sdist`` then ``python -m pip install path/to/shopyo-x.x.x.tar.gz`` where shopyo-... is found in dist/

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

💬 Community: Discord
---------------------
Join the Discord community `Discord Group <https://discord.com/invite/k37Ef6w>`_
