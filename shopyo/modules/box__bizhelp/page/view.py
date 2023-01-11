import json
import os

from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_required
from modules.box__bizhelp.i18n.helpers import get_current_lang
from modules.box__bizhelp.i18n.helpers import lang_keys

from .forms import PageForm
from .models import Page
from shopyo.api.forms import flash_errors
from shopyo.api.module import ModuleHelp

mhelp = ModuleHelp(__file__, __name__)
globals()[mhelp.blueprint_str] = mhelp.blueprint
module_blueprint = globals()[mhelp.blueprint_str]


module_name = mhelp.info["module_name"]

sidebar = [{"text": "sample", "icon": "fa fa-table", "url": ""}]

module_settings = {"sidebar": sidebar}


@module_blueprint.route(mhelp.info["dashboard"] + "/all")
def index_all():
    context = {}
    pages = Page.query.all()

    context.update({"pages": pages})
    return render_template("page/all_pages.html", **context)


@module_blueprint.route(mhelp.info["dashboard"] + "/edit")
def index():
    context = {}
    pages = Page.query.all()

    context.update({"pages": pages})
    return render_template("page/all_pages.html", **context)


@module_blueprint.route("/s/<slug>", methods=["GET"])
def view_page(slug):
    context = {}
    page = Page.query.filter(Page.slug == slug).first()
    form = PageForm(obj=page)

    lang_arg = request.args.get("lang", get_current_lang())

    form.content = page.get_content(lang=lang_arg)
    form.lang.data = lang_arg

    context.update({"page": page, "form": form})
    return render_template("page/view_page.html", **context)


@module_blueprint.route(mhelp.info["dashboard"])
@login_required
def dashboard():
    context = {}
    form = PageForm()

    context.update({"form": form, "module_name": module_name})
    context.update(module_settings)
    return render_template("page/dashboard.html", **context)


@module_blueprint.route("/check_pagecontent", methods=["GET", "POST"])
@login_required
def check_pagecontent():
    if request.method == "POST":
        form = PageForm()
        if not form.validate_on_submit():
            flash_errors(form)
            return redirect(url_for(f"{module_name}.dashboard"))
        toaddpage = Page(
            slug=form.slug.data,
            title=form.title.data,
        )
        toaddpage.insert_lang(form.lang.data, form.content.data)
        toaddpage.save()
        return redirect(url_for(f"{module_name}.dashboard"))
