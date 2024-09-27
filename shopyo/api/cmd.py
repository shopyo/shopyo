"""
commandline utilities functions
"""

import importlib
import os
import re
import subprocess
import sys

import click
from flask.cli import FlaskGroup
from flask.cli import pass_script_info
from init import db
from init import root_path

from shopyo.api.cmd_helper import tryrmcache
from shopyo.api.cmd_helper import tryrmfile
from shopyo.api.cmd_helper import tryrmtree
from shopyo.api.file import get_folders
from shopyo.api.file import trycopytree
from shopyo.api.file import trymkdir
from shopyo.api.file import trymkfile
from shopyo.api.info import printinfo
from shopyo.app import create_app


def _create_shopyo_app(info):
    config_name = info.data.get("config") or "development"
    return create_app(config_name=config_name)


@click.group(cls=FlaskGroup, create_app=_create_shopyo_app)
@click.option("--config", default="development", help="Flask app configuration type")
@pass_script_info
def cli(info, **parmams):
    """CLI for shopyo"""
    printinfo()


@cli.command("new")
def new(help="shopyo new or shopyo new <folder>"):
    """Added only to get the new command for click if i remember well."""
    pass


def clean(app):
    """
    Deletes shopyo.db and migrations/ if present in current working directory.
    Deletes all __pycache__ folders starting from current working directory
    all the way to leaf directory.

    Parameters
    ----------
        - app: flask app that that need to be cleaned

    Returns
    -------
    None
        ...

    """
    SEP_CHAR = "#"
    SEP_NUM = 23

    print(SEP_CHAR * SEP_NUM, end="\n\n")
    print("Cleaning...")

    # getting app context creates the shopyo.db file even if it is not present
    with app.test_request_context():
        db.drop_all()
        db.engine.execute("DROP TABLE IF EXISTS alembic_version;")
        print("[x] all tables dropped")

    tryrmcache(os.getcwd())
    tryrmfile(os.path.join(os.getcwd(), "shopyo.db"), verbose=True)
    tryrmtree(os.path.join(os.getcwd(), "migrations"), verbose=True)


def initialise():
    """
    Create db, migrate, adds default users, add settings

    Parameters
    ----------


    Returns
    -------
    None


    """
    SEP_CHAR = "#"
    SEP_NUM = 23

    print("Creating Db")
    print(SEP_CHAR * SEP_NUM, end="\n\n")
    subprocess.run([sys.executable, "manage.py", "db", "init"], stdout=subprocess.PIPE)

    print("Migrating")
    print(SEP_CHAR * SEP_NUM, end="\n\n")
    subprocess.run(
        [sys.executable, "manage.py", "db", "migrate"], stdout=subprocess.PIPE
    )
    subprocess.run(
        [sys.executable, "manage.py", "db", "upgrade"], stdout=subprocess.PIPE
    )

    print("Collecting static")
    print(SEP_CHAR * SEP_NUM, end="\n\n")
    subprocess.run(
        [sys.executable, "manage.py", "collectstatic"], stdout=subprocess.PIPE
    )

    # Uploads
    print("Uploads")
    print(SEP_CHAR * SEP_NUM, end="\n\n")

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
                except ImportError:
                    # print(e)
                    pass
        else:
            # apps
            try:
                upload = importlib.import_module(f"modules.{folder}.upload")
                upload.upload()
            except ImportError:
                # print(e)
                pass

    print("Done!")


def create_module(modulename, base_path=None):
    """
    creates module with the structure defined in the modules section in docs

    Parameters
    ----------
    modulename: str
        name of module, in alphanumeric-underscore

    Returns
    -------
    None


    """

    if bool(re.match(r"^[\w]+$", modulename)) is False:
        print(
            "Error: modulename is not valid, please use alphanumeric             and"
            " underscore only"
        )
        sys.exit()
    print(f"creating module: {modulename}")
    if not base_path:
        base_path = f"modules/{modulename}"
    trymkdir(base_path)
    trymkdir(f"{base_path}/templates")
    trymkdir(f"{base_path}/templates/{modulename}")
    trymkdir(f"{base_path}/tests")
    trymkdir(f"{base_path}/static")
    test_func_content = """
Please add your functional tests to this file.
"""
    test_model_content = """
Please add your models tests to this file.
"""
    trymkfile(f"{base_path}/tests/test_{modulename}_functional.py", test_func_content)
    trymkfile(f"{base_path}/tests/test_{modulename}_models.py", test_model_content)
    view_content = """
from shopyo.api.module import ModuleHelp
# from flask import render_template
# from flask import url_for
# from flask import redirect
# from flask import flash
# from flask import request

# from shopyo.api.html import notify_success
# from shopyo.api.forms import flash_errors

mhelp = ModuleHelp(__file__, __name__)
globals()[mhelp.blueprint_str] = mhelp.blueprint
module_blueprint = globals()[mhelp.blueprint_str]

@module_blueprint.route("/")
def index():
    return mhelp.info['display_string']

# If "dashboard": "/dashboard" is set in info.json
#
# @module_blueprint.route("/dashboard", methods=["GET"])
# def dashboard():

#     context = mhelp.context()

#     context.update({

#         })
#     return mhelp.render('dashboard.html', **context)
"""
    trymkfile(f"{base_path}/view.py", view_content)
    trymkfile(f"{base_path}/forms.py", "")
    trymkfile(f"{base_path}/models.py", "")
    info_json_content = """{{
        "display_string": "{0}",
        "module_name":"{1}",
        "type": "show",
        "fa-icon": "fa fa-store",
        "url_prefix": "/{1}",
        "author": {{
            "name":"",
            "website":"",
            "mail":""
        }}
}}""".format(
        modulename.capitalize(), modulename
    )
    trymkfile(f"{base_path}/info.json", info_json_content)

    trymkdir(f"{base_path}/templates/{modulename}/blocks")
    trymkfile(f"{base_path}/templates/{modulename}/blocks/sidebar.html", "")
    dashboard_file_content = """
{% extends "shopyo_base/module_base.html" %}
{% set active_page = info['display_string']+' dashboard' %}
{% block pagehead %}
<title></title>
<style>
</style>
{% endblock %}
{% block sidebar %}
{% include info['module_name']+'/blocks/sidebar.html' %}
{% endblock %}
{% block content %}
<br>

<div class="card">
    <div class="card-body">

    </div>
 </div>
{% endblock %}
"""
    trymkfile(
        f"{base_path}/templates/{modulename}/dashboard.html",
        dashboard_file_content,
    )
    global_file_content = """
available_everywhere = {

}
"""
    trymkfile(f"{base_path}/global.py", global_file_content)


def create_box(name):
    """
    creates box with box_info.json

    Parameters
    ----------
    name: str
        name of box, in alphanumeric-underscore

    Returns
    -------
    None


    """
    base_path = f"modules/box__{name}"
    if os.path.exists(base_path):
        print(f"Box {base_path} exists!")
    else:
        trymkdir(base_path)
        info_json_content = """{{
        "display_string": "{0}",
        "box_name":"{1}",
        "author": {{
            "name":"",
            "website":"",
            "mail":""
        }}
    }}""".format(
            name.capitalize(), name
        )
        trymkfile(f"{base_path}/box_info.json", info_json_content)


def create_module_in_box(modulename, boxname):
    """
    creates module with the structure defined in the modules section in docs in
    a box

    Parameters
    ----------
    modulename: str
        name of module, in alphanumeric-underscore

    boxname: str
        name of box, in alphanumeric-underscore

    Returns
    -------
    None


    """
    box_path = os.path.join("modules", boxname)
    module_path = os.path.join("modules", boxname, modulename)

    if not boxname.startswith("box__"):
        print(f"Invalid box {boxname}. Boxes should start with box__")

    elif not os.path.exists(box_path):
        print(f"Box {box_path} does not exists!")
        available_boxes = "\n* ".join(
            [f for f in os.listdir("modules/") if f.startswith("box__")]
        )
        print(f"Available boxes: \n* {available_boxes}")

    elif os.path.exists(module_path):
        print(f"Module {module_path} exists")

    else:
        print(f"Creating module {module_path}")
        create_module(modulename, base_path=module_path)


def createmodulebox(string):
    exit_status = True
    message = ""

    if "/" in string:
        if string.count("/") != 1:
            exit_status = False
            message = "more than one / found in argument"
            return [exit_status, message]
        elif string.count("/") == 1:
            boxname = string.split("/")[0]
            modulename = string.split("/")[1]

            create_module_in_box(modulename, boxname)

    elif string.startswith("box__"):
        create_box(string)

    else:
        create_module(string)

    message = "Created successfully!"
    return [exit_status, message]


def collect_static(target_module="modules", verbose=False):
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

    click.echo("")


if __name__ == "__main__":
    cli()
