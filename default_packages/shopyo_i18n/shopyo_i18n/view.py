from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from shopyo.api.forms import flash_errors
from shopyo.api.html import notify_success
from shopyo.api.models import db
from shopyo.api.module import ModuleHelp
from shopyo.api.security import get_safe_redirect
from flask_login import login_required
from shopyo_i18n.forms import LanguageForm
from shopyo_i18n.models import LangRecord

mhelp = ModuleHelp(__file__, __name__)
globals()[mhelp.blueprint_str] = mhelp.blueprint
module_blueprint = globals()[mhelp.blueprint_str]


@module_blueprint.route("/")
def index():
    return mhelp.info["display_string"]


@module_blueprint.route("/set-lang", methods=["GET"])
def set_lang():
    set_to_lang = request.args.get("lang", "en")
    next_url = request.args.get("next", "/")

    if LangRecord.query.filter(LangRecord.lang_code == set_to_lang).first():
        session["yo_current_lang"] = set_to_lang
        session["yo_default_lang"] = set_to_lang

    return redirect(get_safe_redirect(next_url))


@module_blueprint.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    form = LanguageForm()

    if form.validate_on_submit():
        lang = LangRecord(lang_code=form.lang_code.data, lang_name=form.lang_name.data)
        db.session.add(lang)
        db.session.commit()
        flash(notify_success("Language added!"))
        return redirect(url_for("shopyo_i18n.dashboard"))
    elif form.errors:
        flash_errors(form)

    context = mhelp.context()
    context.update({"langs": LangRecord.query.all(), "form": form})
    return mhelp.render("dashboard.html", **context)


@module_blueprint.route("/delete/<lang_code>", methods=["POST"])
@login_required
def delete(lang_code):
    lang = LangRecord.query.get(lang_code)
    db.session.delete(lang)
    db.session.commit()
    flash(notify_success("Language deleted!"))
    return redirect(url_for("shopyo_i18n.dashboard"))
