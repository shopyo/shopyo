from flask import session
from modules.box__bizhelp.i18n.helpers import lang_keys

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
    return mhelp.info["display_string"]


@module_blueprint.route("/set-lang", methods=["GET"])
def set_lang():

    try:
        set_to_lang = request.args["lang"]
        return_url = request.args["return"]

        if set_to_lang in lang_keys():
            session["yo_current_language"] = set_to_lang

            return redirect(return_url)
    except KeyError:
        pass

    return mhelp.info["display_string"]


# If "dashboard": "/dashboard" is set in info.json
#
# @module_blueprint.route("/dashboard", methods=["GET"])
# def dashboard():

#     context = mhelp.context()

#     context.update({

#         })
#     return mhelp.render('dashboard.html', **context)
