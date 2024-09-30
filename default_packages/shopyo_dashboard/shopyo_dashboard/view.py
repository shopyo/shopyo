import json
import os

from flask import current_app
from flask import flash
from flask import render_template
from flask_login import login_required
from shopyo_appadmin.admin import admin_required
from shopyo_auth.decorators import check_confirmed

from shopyo.api.html import notify_success
from shopyo.api.module import ModuleHelp

mhelp = ModuleHelp(__file__, __name__)
globals()[mhelp.blueprint_str] = mhelp.blueprint
module_blueprint = globals()[mhelp.blueprint_str]


all_info = {}


import importlib
import pkgutil



@module_blueprint.route("/")
@login_required
@check_confirmed
@admin_required
def index():
    context = {}

    # for plugins

    for plugin in current_app.extensions:
        if plugin.startswith('shopyo_'):
            all_info[plugin] = current_app.extensions[plugin].get_info()

    # for local folders
    for folder in os.listdir(os.path.join(current_app.config["BASE_DIR"], "modules")):
        if folder.startswith("__"):
            continue
        elif folder.startswith("box__"):
            for sub_folder in os.listdir(
                os.path.join(current_app.config["BASE_DIR"], "modules", folder)
            ):
                if sub_folder in ["dashboard"]:
                    continue
                if sub_folder.startswith("__"):  # ignore __pycache__
                    continue
                elif sub_folder.endswith(".json"):  # box_info.json
                    continue
                with open(
                    os.path.join(
                        current_app.config["BASE_DIR"],
                        "modules",
                        folder,
                        sub_folder,
                        "info.json",
                    )
                ) as f:
                    module_info = json.load(f)
                    all_info[sub_folder] = module_info
        else:
            if folder not in ["dashboard"]:
                with open(
                    os.path.join(
                        current_app.config["BASE_DIR"],
                        "modules",
                        folder,
                        "info.json",
                    )
                ) as f:
                    module_info = json.load(f)
                    all_info[folder] = module_info

    print(all_info)

    context["all_info"] = all_info
    flash(notify_success("Notif test"))
    return render_template("shopyo_dashboard/index.html", **context)
