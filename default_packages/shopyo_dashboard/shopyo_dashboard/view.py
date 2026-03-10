import json
import os
import datetime

from flask import current_app
from flask import render_template
from flask_login import login_required
from shopyo_appadmin.admin import admin_required
from shopyo_auth.decorators import check_confirmed

from shopyo.api.module import ModuleHelp

mhelp = ModuleHelp(__file__, __name__)
globals()[mhelp.blueprint_str] = mhelp.blueprint
module_blueprint = globals()[mhelp.blueprint_str]


@module_blueprint.route("/")
@login_required
@check_confirmed
@admin_required
def index():
    all_info = {}

    # 1. Collect info from extensions
    for plugin in current_app.extensions:
        if plugin.startswith("shopyo_") and hasattr(
            current_app.extensions[plugin], "get_info"
        ):
            try:
                all_info[plugin] = current_app.extensions[plugin].get_info()
            except Exception:
                continue

    # 2. Collect info from local modules
    modules_path = os.path.join(current_app.config["BASE_DIR"], "modules")
    if os.path.exists(modules_path):
        for folder in os.listdir(modules_path):
            if folder.startswith("__") or folder == "dashboard":
                continue

            abs_path = os.path.join(modules_path, folder)

            # Handle box__ modules
            if folder.startswith("box__"):
                for sub_folder in os.listdir(abs_path):
                    if sub_folder.startswith("__") or sub_folder.endswith(".json"):
                        continue

                    info_file = os.path.join(abs_path, sub_folder, "info.json")
                    if os.path.exists(info_file):
                        with open(info_file) as f:
                            all_info[sub_folder] = json.load(f)
            else:
                info_file = os.path.join(abs_path, "info.json")
                if os.path.exists(info_file):
                    with open(info_file) as f:
                        all_info[folder] = json.load(f)

    return render_template(
        "shopyo_dashboard/index.html",
        all_info=all_info,
        current_year=datetime.datetime.now().year,
    )
