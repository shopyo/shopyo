version_info = (4, 11, 1)
__version__ = ".".join([str(v) for v in version_info])


"""
4.11.1

- explicit errors on missing imports while looking for create_app

4.11.0

- auth is now shopyo_auth
- dashboard is now shopyo_dashboard
- app admin is now shopyo_appadmin

4.10.0

- base module now ships in a separate package: shopyo_base

4.9.5

- initialize supports sqlalchemy 2.0

4.9.4

- loosen sqlalchemy requirment; initialize still expected to fail, but package usable

4.9.3

- Remove marshmallow from deps

4.9.2

- Fix missing import

4.9.1

- Important security fixes to box__default

4.9.0

- Provide more info on missing installed_packages
- Bound SQLAlchemy version

4.8.6

- Fixes for sqlalchemy db & other upgrade supports

4.8.5

- Tests and docs fixes

4.8.4

- Implement debug mode
- Fix docs builds fail

4.8.3

- Fix load erros instead of passing

4.8.2

- Fix admin required on dashbaord

4.8.1

- Fix import errors

4.8.0

- box__bizhelp removed
- i18n and page moved to box__default

4.7.0

- i18n package
- page module revamp

4.6.0

- Packages added!!!

4.5.9

- fix autoload for packages

4.5.8

- fix key error in cmd_helper

4.5.7

- fix verbose=vebose

4.5.6

- rm app.txt for new projects

4.5.5

- Fix empty static folder for projects not using -m

4.5.4

- Refactor move register_devstatic to api

4.5.3

- Refactor load_extensions to init.py

4.5.2

- Fix static path

4.5.1

- Fix path parameter in api.assets.get_static

4.5.0

- Add url_prefix conflict detection to audit command

4.4.3

- Fix initialise, add SHOPYO_CONFIG_PROFILE env var to denote configuration profiles

4.4.2

- Fix email-validator version

4.4.1

- Fix app.py on new projects
- Fix validator required in reqs
- Fix remove settings functions from www.view

4.4.0

- Add global configs via module

4.3.7

- Remove 3.6 support

"""
