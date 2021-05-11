## Unreleased

## Version 4.1.1
Released 2021-05-10
* Fixed `python maanage.py COMMAND` not working for any commands other than `rundebug` or `initilaise`
commands as explained in #13 

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

## Version 3.9.2
Released 2021-03-15

## Version 3.9.1
Released 2021-03-15

## Version 3.9.0
Released 2021-03-01

## Version 3.8.41
Released 2021-02-25

## Version 3.8.31
Released 2021-02-24

## Version 3.8.1
Released 2021-02-24

## Version 3.8.0
Released 2021-02-24

## Version 3.4.2
Released 2021-01-20

## Version 3.3.2
Released 2021-01-09

## Version 3.0.0
Released 2020-12-23


- modules 100% configured from info.json: added dashboard, display_string and module_name to info.json
- startapp templates changed
- login has warning notif on bad login
- added commented out imports on view.py template
- shopyo command activates manage.py commands