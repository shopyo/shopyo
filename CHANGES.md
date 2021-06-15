## Unreleased

* Add click cmds `shopyo rundebug` and `shopyo runserver` as in Django. See [#51](https://github.com/shopyo/shopyo/issues/51)
* Rename `createmodule` cmd to `startapp` to mimic Django
* Move the `config.json` creation to inside `create_app`. Remove environment key from `config.json` as all Flask related config should either be in `config.py`, `.env` or `.flaskenv`
* Clean up `app.py` with functions for each `create_app` task and remove app creation inside `app.py`
* Fix the import issues that was causing [#37](https://github.com/shopyo/shopyo/issues/37). Now `shopyo new` command will not work but this is moved to [shopyo-factory](https://github.com/shopyo/shopyo-factory)
* add changelog link to `setup.cfg` so that it shows on Shopyo PyPi page

## Version 4.1.2

Released 2021-05-19

* repaced Alabaster sphinx theme with Furo
* pinned the pallet projects related dependencies to older versions as the latest release breaks the project

## Version 4.1.1

Released 2021-05-10

* Fixed `python maanage.py COMMAND` not working for any commands other than `rundebug` or `initilaise` commands as explained in #13

## Version 4.1.0

Released 2021-05-07

* refactored cli to use `Click` for individual commands. See [issue #473](https://github.com/Abdur-rahmaanJ/shopyo/issues/473) of the archived `shopyo` repo
* added `shopyo createmodule [OPTIONS] MODULENAME [BOXNAME]` cli to allow an option creating module with/without box in one command rather than doing `shopyo startbox BOXNAME` followed by `shopyo startsubapp MODUELNAME in BOXNAME`
* extend `shopyo new PROJNAME` command to `shopyo new [OPTIONS] [PROJNAME]` allowing the optional PROJNAME to create
the new project of same name as base directory name
* added `cli.py` with `shopyo new [OPTIONS] [PROJNAME]` command to allow users to add their click commands with example commands included. See [issue #474](https://github.com/Abdur-rahmaanJ/shopyo/issues/474) of the archived `shopyo` repo
* added verbose (`-v or --verbose`) option for each of the cli command to print extra information when running
any cli command
* made the printout of the cli commands to be consistent

## Version 3.9.4

Released 2021-03-17
