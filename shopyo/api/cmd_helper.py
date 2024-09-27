"""
Helper utility functions for commandline api
"""

import importlib
import json
import os
import re
import sys
from importlib.metadata import version
from subprocess import run

import click
from flask import current_app

from shopyo.api.cli_content import get_dashboard_html_content
from shopyo.api.cli_content import get_global_py_content
from shopyo.api.cli_content import get_module_view_content
from shopyo.api.constants import SEP_CHAR
from shopyo.api.constants import SEP_NUM
from shopyo.api.file import get_folders
from shopyo.api.file import last_part_of_path
from shopyo.api.file import path_exists
from shopyo.api.file import trycopytree
from shopyo.api.file import trymkdir
from shopyo.api.file import trymkfile
from shopyo.api.file import tryrmcache
from shopyo.api.file import tryrmfile
from shopyo.api.file import tryrmtree


def _clean(verbose=False, clear_migration=True, clear_db=True):
    """
    Deletes shopyo.db and migrations/ if present in current working directory.
    Deletes all __pycache__ folders starting from current working directory
    all the way to leaf directory.

    Parameters
    ----------
        - verbose: flag to indicate whether to print to result of clean to
            stdout or not.
        - clear_migration: flag to indicate if migration folder is to be deleted or not
        - clear_db: flag indicating if db is to be cleared or not
        - db: db to be cleaned

    Returns
    -------
    None
        ...

    """
    click.echo("Cleaning...")
    click.echo(SEP_CHAR * SEP_NUM)
    try:
        db = current_app.extensions["sqlalchemy"].db
    except:
        db = current_app.extensions["sqlalchemy"]

    if clear_db:
        db.drop_all()
        sqlalchemy_version = version("sqlalchemy").split(".")

        sql = "DROP TABLE IF EXISTS alembic_version;"
        if int(sqlalchemy_version[0]) <= 1:
            db.engine.execute(sql)
        else:
            from sqlalchemy import text

            with db.engine.begin() as conn:
                result = conn.execute(text(sql))
                conn.commit()

        tryrmfile(os.path.join(os.getcwd(), "shopyo.db"), verbose=verbose)
        if verbose:
            click.echo("[x] all tables dropped")
    elif clear_db is False:
        if verbose:
            click.echo("[ ] db clearing skipped")

    tryrmcache(os.getcwd(), verbose=verbose)

    if clear_migration:
        tryrmtree(os.path.join(os.getcwd(), "migrations"), verbose=verbose)
    elif clear_migration is False:
        if verbose:
            click.echo("[ ] migration folder delete skipped")


def _collectstatic(target_module="modules", verbose=False):
    """
    Copies ``module/static`` into ``/static/modules/module``.
    In static it becomes like

    ::

       static/
            modules/
                box_something/
                    modulename
                modulename2


    Parameters
    ----------
    target_module: str
        name of module, in alphanumeric-underscore,
        supports ``module`` or ``box__name/module``

    Returns
    -------
    None

    """
    click.echo("Collecting static...")
    click.echo(SEP_CHAR * SEP_NUM)

    root_path = os.getcwd()
    static_path = os.path.join(root_path, "static")

    # if target_module path does not start with 'modules\' add it to as a
    # prefix to the target_module path
    if target_module != "modules":
        # normalize the target_module path to be same as that of OS
        target_module = re.split(r"[/|\\]+", target_module)
        target_module_start = target_module[0]
        target_module = os.path.join(*target_module)

        # add the modules folder to start of target_module incase it is not
        # already present in the path
        if target_module_start != "modules":
            target_module = os.path.join("modules", target_module)

    # get the full path for modules (the src). Defaults to ./modules
    modules_path = os.path.join(root_path, target_module)

    # get the full path of static folder to copy to (the dest).
    # always ./static/modules
    modules_path_in_static = os.path.join(static_path, "modules")

    # terminate if modules_path (i.e. src to copy static from) does not exist
    if not os.path.exists(modules_path):
        click.echo(f"[ ] path: {modules_path} does not exist")
        sys.exit(1)

    # clear ./static/modules before coping to it
    tryrmtree(modules_path_in_static, verbose=verbose)

    # look for static folders in all project
    for folder in get_folders(modules_path):
        if folder.startswith("box__"):
            box_path = os.path.join(modules_path, folder)
            for subfolder in get_folders(box_path):
                module_name = subfolder
                module_static_folder = os.path.join(box_path, subfolder, "static")
                if not os.path.exists(module_static_folder):
                    continue
                module_in_static_dir = os.path.join(
                    modules_path_in_static, folder, module_name
                )

                # copy from ./modules/<box__name>/<submodule> to
                # ./static/modules
                trycopytree(module_static_folder, module_in_static_dir, verbose=verbose)
        else:
            path_split = ""

            # split the target module if default target_module path name is
            # not used
            if target_module != "modules":
                path_split = re.split(r"[/|\\]", target_module, maxsplit=1)
                path_split = path_split[1]

            if folder.lower() == "static":
                module_static_folder = os.path.join(modules_path, folder)
                module_name = path_split
            else:
                module_static_folder = os.path.join(modules_path, folder, "static")
                module_name = os.path.join(path_split, folder)

            if not os.path.exists(module_static_folder):
                continue
            module_in_static_dir = os.path.join(modules_path_in_static, module_name)
            tryrmtree(module_in_static_dir, verbose=verbose)
            trycopytree(module_static_folder, module_in_static_dir, verbose=verbose)

    # load packages

    try:
        from init import installed_packages
    except ImportError:
        click.echo(
            "This version of Shopyo requires that\n"
            "init.py contains the line\n"
            "installed_packages = []\n"
            "please add it."
        )
        sys.exit()
    for plugin in installed_packages:
        try:
            plugin_mod = importlib.import_module(plugin)
            plugin_folder_path = plugin_mod.view.mhelp.dirpath
            plugin_static_folder = os.path.join(plugin_folder_path, "static")

            if os.path.exists(plugin_static_folder):
                plugin_in_static_dir = os.path.join(modules_path_in_static, plugin)
                tryrmtree(plugin_in_static_dir, verbose=verbose)
                trycopytree(plugin_static_folder, module_in_static_dir, verbose=verbose)
                if verbose:
                    click.echo(f"[x] collected static from {plugin}")
            else:
                if verbose:
                    click.echo(f"[ ] static folder not found: {plugin_static_folder}")
        except Exception as e:
            if verbose:
                click.echo(f"[ ] statoc {e}")

    click.echo("")


def _upload_data(verbose=False):
    click.echo("Uploading initial data to db...")
    click.echo(SEP_CHAR * SEP_NUM)

    root_path = os.getcwd()

    for folder in os.listdir(os.path.join(root_path, "modules")):
        if folder.startswith("__"):  # ignore __pycache__
            continue
        if folder.startswith("box__"):
            # boxes
            for sub_folder in os.listdir(os.path.join(root_path, "modules", folder)):
                if sub_folder.startswith("__"):  # ignore __pycache__
                    continue
                elif sub_folder.endswith(".json"):  # box_info.json
                    continue

                try:
                    upload = importlib.import_module(
                        f"modules.{folder}.{sub_folder}.upload"
                    )
                    upload.upload()
                except ImportError as e:
                    if verbose:
                        click.echo(f"[ ] {e}")
        else:
            # apps
            try:
                upload = importlib.import_module(f"modules.{folder}.upload")
                upload.upload()
            except ImportError as e:
                if verbose:
                    click.echo(f"[ ] {e}")

    # load packages

    from init import installed_packages

    for plugin in installed_packages:
        try:
            plugin_mod = importlib.import_module(f"{plugin}.upload")
            plugin_mod.upload()
            if verbose:
                click.echo(f"[x] uploaded from {plugin}")
        except Exception as e:
            if verbose:
                click.echo(f"[ ] upload info: {e}")

    click.echo("")


def _create_box(boxname, verbose=False):
    base_path = os.path.join("modules", boxname)
    trymkdir(base_path, verbose=verbose)

    info_json = {
        "display_string": boxname.capitalize(),
        "box_name": boxname,
        "author": {"name": "", "website": "", "mail": ""},
    }

    box_info = os.path.join(base_path, "box_info.json")

    with open(box_info, "w", encoding="utf-8") as f:
        json.dump(info_json, f, indent=4, sort_keys=True)

    if verbose:
        click.echo("'box_info.json' content:")
        click.echo(json.dumps(info_json, indent=4, sort_keys=True))

    click.echo(f"{boxname} created!")


def _create_module(modulename, base_path=None, verbose=False):
    """creates module with the structure defined in the modules section in docs
    Assume valid modulename i.e modulename does not start with ``box__`` and
    modulename consist only of alphanumeric characters or underscore

    Parameters
    ----------
    modulename: str
        name of module, in alphanumeric-underscore

    Returns
    -------
    None

    """

    click.echo(f"creating module: {modulename}")
    click.echo(SEP_CHAR * SEP_NUM)

    if base_path is None:
        base_path = os.path.join("modules", modulename)

    # create the module with directories templates, tests, static
    trymkdir(base_path, verbose=verbose)
    trymkdir(os.path.join(base_path, "templates"), verbose=verbose)
    trymkdir(os.path.join(base_path, "templates", modulename), verbose=verbose)
    trymkdir(os.path.join(base_path, "tests"), verbose=verbose)
    trymkdir(os.path.join(base_path, "static"), verbose=verbose)

    # create functional test and unit test files for the module
    test_func_path = os.path.join(
        base_path, "tests", f"test_{modulename}_functional.py"
    )
    test_models_path = os.path.join(base_path, "tests", f"test_{modulename}_models.py")
    test_func_content = "# Please add your functional tests to this file.\n"
    test_model_content = "# Please add your models tests to this file.\n"
    trymkfile(test_func_path, test_func_content, verbose=verbose)
    trymkfile(test_models_path, test_model_content, verbose=verbose)

    # create view.py, forms.py and model.py files inside the module
    trymkfile(
        os.path.join(base_path, "view.py"), get_module_view_content(), verbose=verbose
    )
    trymkfile(os.path.join(base_path, "forms.py"), "", verbose=verbose)
    trymkfile(os.path.join(base_path, "models.py"), "", verbose=verbose)

    # create info.json file inside the module
    info_json = {
        "display_string": modulename.capitalize(),
        "module_name": modulename,
        "type": "show",
        "fa-icon": "fa fa-store",
        "url_prefix": f"/{modulename}",
        "author": {"name": "", "website": "", "mail": ""},
    }
    info_json_path = os.path.join(base_path, "info.json")
    with open(info_json_path, "w", encoding="utf-8") as f:
        json.dump(info_json, f, indent=4, sort_keys=True)

    if verbose:
        click.echo(f"[x] file created at '{info_json_path}' with content: ")
        click.echo(json.dumps(info_json, indent=4, sort_keys=True))

    # create the sidebar.html inside templates/blocks
    blocks_path = os.path.join(base_path, "templates", modulename, "blocks")
    trymkdir(blocks_path, verbose=verbose)
    trymkfile(os.path.join(blocks_path, "sidebar.html"), "", verbose=verbose)

    # create the dashboard.html inside templates/MODULENAME
    trymkfile(
        os.path.join(base_path, "templates", modulename, "dashboard.html"),
        get_dashboard_html_content(),
        verbose=verbose,
    )

    # create the global.py files inside the module
    trymkfile(
        os.path.join(base_path, "global.py"), get_global_py_content(), verbose=verbose
    )


def _run_app(mode):
    """helper command for running shopyo flask app in debug/production mode"""
    app_path = os.path.join(os.getcwd(), "app.py")

    if not os.path.exists(app_path):
        click.secho(f"Unable to find `app.py` in {os.getcwd()}", fg="red")
        sys.exit(1)

    os.environ["FLASK_APP"] = f"app:create_app('{mode}')"
    os.environ["FLASK_ENV"] = mode
    os.environ["ENV"] = mode
    run(["flask", "run"])


def _check_modules_path(root_path):
    modules_path = os.path.join(root_path, "modules")
    if not path_exists(modules_path):
        click.echo("Modules folder not found!")
        sys.exit()


def _url_prefix_exists(url_prefix, found_url_prefixes):
    for data in found_url_prefixes:
        if url_prefix == data["url_prefix"]:
            return {"status": True, "data": data}
    return {"status": False, "data": dict()}


def _verify_app(app_path, found_url_prefixes, box_name=None):
    app_folder = last_part_of_path(app_path)

    audit_info = {"path": app_path, "issues": []}

    # verify info.json
    if not path_exists(os.path.join(app_path, "info.json")):
        audit_info["issues"].append("severe: info.json not found")
    else:
        with open(os.path.join(app_path, "info.json")) as f:
            json_data = json.load(f)

        _url_prefix_exists(json_data["url_prefix"], found_url_prefixes)

        to_check_keys = ["module_name", "url_prefix"]
        not_found = []
        for key in to_check_keys:
            if key not in json_data:
                not_found.append(key)
                msg = f"severe: key {key} not found in info.json"
                audit_info["issues"].append(msg)

        if ("module_name" not in not_found) and ("url_prefix" not in not_found):
            if (json_data["module_name"].strip() == "") or (
                json_data["url_prefix"].strip() == ""
            ):
                msg = (
                    "sus: module_name and url_prefix in info.json must not be empty"
                    " ideally"
                )
                audit_info["issues"].append(msg)

        if "module_name" not in not_found:
            if {json_data["module_name"], app_folder} != {app_folder}:
                msg = """severe: currently module_name "{}" in info.json and app folder "{}" must have the same value""".format(
                    json_data["module_name"], app_folder
                )
                audit_info["issues"].append(msg)

        url_prefix_exists = _url_prefix_exists(
            json_data["url_prefix"], found_url_prefixes
        )

        if url_prefix_exists["status"] is True:
            msg = (
                f"warning: url_prefix '{json_data['url_prefix']}' exists in"
                f" '{app_path}' and '{url_prefix_exists['data']['path']}'"
            )
            audit_info["issues"].append(msg)
        else:
            found_url_prefixes.append(
                {"path": app_path, "url_prefix": json_data["url_prefix"]}
            )

    # verify components

    if not path_exists(os.path.join(app_path, "templates")):
        audit_info["issues"].append("warning: templates folder not found")

    if not path_exists(os.path.join(app_path, "view.py")):
        audit_info["issues"].append("severe: view.py not found")

    if not path_exists(os.path.join(app_path, "forms.py")):
        audit_info["issues"].append("info: forms.py not found")

    if not path_exists(os.path.join(app_path, "models.py")):
        audit_info["issues"].append("info: models.py not found")

    if not path_exists(os.path.join(app_path, "global.py")):
        audit_info["issues"].append("info: global.py not found")

    return audit_info


def _verify_box(box_path):
    audit_info = {"issues": []}

    # verify box_info.json
    if not path_exists(os.path.join(box_path, "box_info.json")):
        audit_info["issues"].append("warning: box_info.json not found")
    else:
        with open(os.path.join(box_path, "box_info.json")) as f:
            json_data = json.load(f)

        to_check_keys = ["box_name"]

        for key in to_check_keys:
            if key not in json_data:
                msg = f"severe: key {key} not found in box_info.json"
                audit_info["issues"].append(msg)

    return audit_info


def _check_apps(root_path, found_url_prefixes):
    issues_found = []

    modules_path = os.path.join(root_path, "modules")
    apps = get_folders(modules_path)
    apps = [a for a in apps if not a.startswith("__") and not a.startswith("box__")]

    for app in apps:
        app_path = os.path.join(modules_path, app)
        app_issues = _verify_app(app_path, found_url_prefixes)
        issues_found.append(app_issues)

    return issues_found


def _check_boxes(root_path, found_url_prefixes):
    box_issues = []

    modules_path = os.path.join(root_path, "modules")
    boxes = get_folders(modules_path)
    boxes = [b for b in boxes if b.startswith("box__")]

    for b in boxes:
        box_info = {"path": os.path.join(modules_path, b), "apps_issues": []}
        box_info["issues"] = _verify_box(os.path.join(modules_path, b))["issues"]

        for app in get_folders(os.path.join(modules_path, b)):
            app_issues = _verify_app(
                os.path.join(modules_path, b, app), found_url_prefixes, box_name=b
            )
            box_info["apps_issues"].append(app_issues)
        box_issues.append(box_info)

    return box_issues


def _audit(warning, info, severe):
    """
    checks if modules are corrupted
    """
    issue_type = {"warning": warning, "info": info, "severe": severe}
    found_url_prefixes = []

    root_path = os.getcwd()
    _check_modules_path(root_path)
    apps_issues = _check_apps(root_path, found_url_prefixes)
    boxes_issues = _check_boxes(root_path, found_url_prefixes)

    click.echo("Running audit ...")

    click.echo("Checking apps ...")
    for app_issue in apps_issues:
        click.echo(app_issue["path"])
        for issue in app_issue["issues"]:
            if issue_type[issue.split(":")[0]]:
                click.echo("    " + issue)
        click.echo("")

    for box_issue in boxes_issues:
        click.echo(box_issue["path"])
        for issue in box_issue["issues"]:
            if issue_type[issue.split(":")[0]]:
                click.echo("    " + issue)

        for app_issue in box_issue["apps_issues"]:
            click.echo("    " + app_issue["path"])
            for issue in app_issue["issues"]:
                if issue_type[issue.split(":")[0]]:
                    click.echo("        " + issue)
        click.echo("")

    click.echo("Audit finished!")


def _verify_app_name(app_name):
    if (app_name.startswith("box__")) and (app_name.count("/") != 1):
        return False

    if app_name.endswith("/"):
        return False

    return True


def name_is_box(app_name):
    if app_name.startswith("box__"):
        return True

    return False


def _rename_app(old_app_name, new_app_name):
    # box_
    if old_app_name.startswith("box") and not old_app_name.startswith("box__"):
        click.echo('Box names start with two __, example: "box__default"')
        sys.exit()
    if new_app_name.startswith("box") and not new_app_name.startswith("box__"):
        click.echo('Box names start with two __, example: "box__default"')
        sys.exit()

    if (not _verify_app_name(old_app_name)) and (not _verify_app_name(new_app_name)):
        click.echo('App names should be in the format "app" or "box_name/app"')
        sys.exit()

    root_path = os.getcwd()
    modules_path = os.path.join(root_path, "modules")

    if name_is_box(old_app_name):
        box_name = old_app_name.split("/")[0]
        if name_is_box(new_app_name):
            app_part = old_app_name.split("/")[1]
            new_app_name.split("/")[1]

        if not path_exists(os.path.join(modules_path, box_name, app_part)):
            click.echo(f"App {old_app_name} does not exist")
            sys.exit()

    try:
        os.rename(
            os.path.join(modules_path, old_app_name),
            os.path.join(modules_path, new_app_name),
        )

        with open(os.path.join(modules_path, new_app_name, "info.json")) as f:
            json_data = json.load(f)

        with open(os.path.join(modules_path, new_app_name, "info.json"), "w+") as f:
            if name_is_box(new_app_name):
                module_name = new_app_name.split("/")[1]
            else:
                module_name = new_app_name
            json_data["module_name"] = module_name
            json.dump(json_data, f, indent=4)

        click.echo(f"Renamed app {old_app_name} to {new_app_name}")
    except Exception as e:
        raise e
