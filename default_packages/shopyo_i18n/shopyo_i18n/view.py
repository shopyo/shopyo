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
from shopyo_settings.helpers import get_setting
from shopyo_settings.helpers import set_setting

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

    if LangRecord.query.filter(LangRecord.lang == set_to_lang).first():
        session["yo_current_lang"] = set_to_lang
        session["yo_default_lang"] = set_to_lang

    return redirect(get_safe_redirect(next_url))


@module_blueprint.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        new_lang = request.form.get("language")
        if new_lang:
            set_setting("DEFAULT_LANGUAGE", new_lang)
            flash(notify_success(f"Default language updated to {new_lang}!"))
            return redirect(url_for("shopyo_i18n.dashboard"))

    languages = ["en", "fr", "es", "de", "it"]
    current_language = get_setting("DEFAULT_LANGUAGE") or "en"

    context = mhelp.context()
    context.update(
        {
            "languages": languages,
            "current_language": current_language,
        }
    )
    return mhelp.render("dashboard.html", **context)


@module_blueprint.route("/delete/<lang_code>", methods=["POST"])
@login_required
def delete(lang_code):
    records = LangRecord.query.filter(LangRecord.lang == lang_code).all()
    for record in records:
        db.session.delete(record)
    db.session.commit()
    flash(notify_success(f"All records for {lang_code} deleted!"))
    return redirect(url_for("shopyo_i18n.dashboard"))
