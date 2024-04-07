## Unreleased

### Feat

- support sqlalchemy 2.0

## 4.9.4 (2024-04-04)

## 4.9.3 (2023-08-24)

## 4.9.2 (2023-08-22)

### Fix

- import error in i18n

## 4.9.1 (2023-08-22)

### Fix

- missing imports in i18n
- secure admin access to theme module
- secure admin access to page module
- dashboard module route

## 4.9.0 (2023-08-17)

### Feat

- errors (#145)
- debug mode

### Fix

- install deps
- Add wsgi.py as example
- Add autoapp as example

## v4.8.3 (2023-01-13)

### Fix

- dashboard open to non admin
- security alert
- **3.5.7**: upload key

## v4.5.2 (2022-04-16)

### Feat

- add url_conflict detection to audit command, closes #103 (#108)

### Fix

- get_static path not from templates
- serving static assets via api.assets.get_static

## v4.4.3 (2022-04-12)

### Fix

- initialise command failing
- email-validator version pining

## v4.4.1 (2022-04-11)

### Feat

- rename command for boxes and apps (#93)

### Fix

- adjust audit warning levels (#97)
- remove 3.6 for tox
- remove 3.6 for tests
- removed db-dependent function to render default www page
- shopyo image banner in readme
- commented out failing tests

## v4.3.2 (2022-04-09)

### Feat

- shopyo audit (#90)

### Fix

- tests
- tests

### Refactor

- move email from auth to api (#89)
- create assets folder

## v4.2.0 (2021-11-24)

## v4.1.3 (2021-10-26)

### Feat

- added commitizen to repo

### Fix

- add no-action flag
- clear migrations folder
- Improve homepage wording

## v4.1.2 (2021-05-19)

### Feat

- api.templates.yo_render
- cli.py is added
that allows users to add their own project command

### Fix

- version
- version
- style
- test syntax
- test for new command
- new command: shopyo.png
- Set logo to shopyo.png
- adding FLASK_APP is causing importError which causes shopyo initialise to fail. Commented that part for now
- auto create config
- tests
- collecstatic args not consistent with collectstatic
- sqlalchemy issue
- path bug
- path bug
- merge

### Refactor

- add the shopyo info message before each command
- rename files and commmands
- delete unused files
- remove commented out code
- new command comaplete.
- update manage.py to match new cli
- new2 cli now added with basic tests
- add createmodule command
- add the new click command for collectstatic to replace the old on
- clean and write the shopyo initialise cmd
- use click for cli insteade of argv parsing

## v3.9.0 (2021-03-01)

### Feat

- rm ecommerce
- add email confirmation disable option in configs
- add email confirmation
- added uploads protocol
- collectstatic command
- announcement module completed
- add CRUD DB model and other DB utilities

### Fix

- new project README
- init docs
- api.init -> init
- errors
- errors
- forgot to commit pytest.ini file
- local workflow - pull_request
- local workflow
- local workflow
- rm files
- tests failing
- stable
- add shopyo as req
- virtual env not needed for new command
- README
- new command
- PR #396 tests failing and code not compiling.
- Added old admin module as appadmin
- all tests passing
- style
- 124 passing
- not redirect for login
- remove testing endpoint checks
- add flask-admin to requirements
- remove requests package requests package removed from requirements.txt and dev_requirements.txt fixes #383
- use thread join for testing send_async_email
- unused imports
- unreacheableline
- env now reads from json
- added get_self_static in module help
- docs + black
- flake8 and alerts where possible
- #340 merge caused unable to compile code now fixed
- running test does not clear shopyo.db
- theme path in theme/view.py
- lint
- login to auth renaming
- themes to static folder
- remove coverage report command as not needed
- error in the coverage run command
- linting errors
- added panel-control for back theme
- Added front theme in front folder (themes/front/...)
- remove theme info from app.py
- add check for anonymous user; correct flash message
- scrolling for long content
- failing test
- review issues with branch
- style errors
- replace pycodestyle with flake8
- add the SERVER_NAME in test config to allow url_for to be used without errors
- update tox to fix test warning. add tox to dev_requirements

### Refactor

- use intance folder or .env to hide secrets
- separate requirements.txt and dev_requirements.txt
- update clean cmd arg and add tests
- readable tests for category module
- admin test with less code and easier to read
- change the name of crud db model
- add the crud helper class for admin models

## v3.3.6 (2021-01-09)

### Fix

- #221 message not flashing after contact form submit
- please login for access using shopyo notifications
- still delete category bug. closes #234
- modified requirements.txt path for setup.py
- change import statement layout, update travis
- remove the deprecaited yield fixture call causing warning
- partial alerts
- merge conflict on 2nd commit of previous branch
- tests
- correct the linting
- sphinx build command should be before changing directory
- marshmallow_sqlalchemy broken in python 3.5. Removing python 3.5 check
- dev_requriements.txt was misspelled in .travis.yml
- fixed the python linting errors
- docs
- add global.py in modules and removed dummy folder
- get_symbol_currency not found
- add missing packages in dev-requiremnts.txt
- screenshot update

## v3.0.0 (2020-12-22)

### Fix

- conflict
- tests
- add first name and lastname
- styles formatting
- category+subcategory+product addition+product image management, TODO: fix delete of category and subcategory
- rogue empty comment removed
- www now points to / | public facing pages can access header and footer of theme | global vars injected in one place only
- startup command
- startapp command
- picture upload optional
- product pictures completed

## v2.0.0 (2020-11-03)

### Fix

- page dashboard + icon colors

## v1.2.4 (2020-10-09)

### Feat

- added manufacturer details in people module

### Refactor

- checking module name to follow certain constraints

## v1.1.7 (2020-10-04)

### Fix

- Several of issues found on products module are fixed - enhanced
- Several of issues found on products module are fixed
- 138

## v1.2.0 (2020-03-29)

## 1.0.0 (2020-03-08)
