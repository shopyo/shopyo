version_info = (4, 5, 8)
__version__ = ".".join([str(v) for v in version_info])


"""
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
