from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_required
from init import db
from shopyo_appadmin.admin import admin_required
from shopyo_i18n.helpers import get_current_lang

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
@login_required
@admin_required
def index_all():
    context = {}
    pages = Page.query.all()

    context.update({"pages": pages})
    return render_template(f"{module_name}/all_pages.html", **context)


@module_blueprint.route(mhelp.info["dashboard"] + "/all-pages")
@login_required
@admin_required
def index():
    context = {}
    pages = Page.query.all()

    context.update({"pages": pages})
    return render_template(f"{module_name}/all_pages.html", **context)


@module_blueprint.route("dashboard/s/<slug>", methods=["GET"])
@login_required
@admin_required
def view_page_dashboard(slug):
    context = {}
    page = Page.query.filter(Page.slug == slug).first()
    form = PageForm(obj=page)

    lang_arg = request.args.get("lang", get_current_lang())

    form.content = page.get_content(lang=lang_arg)
    form.lang.data = lang_arg

    context.update({"page": page, "form": form})
    return render_template(f"{module_name}/view_page_dashboard.html", **context)


@module_blueprint.route("/s/<slug>", methods=["GET"])
def view_page(slug):
    context = {}
    page = Page.query.filter(Page.slug == slug).first()
    context.update({"page": page})
    return render_template(f"{module_name}/view_page.html", **context)


@module_blueprint.route(mhelp.info["dashboard"])
@login_required
@admin_required
def dashboard():
    context = {}
    form = PageForm()

    context.update({"form": form, "module_name": module_name})
    context.update(module_settings)
    return render_template(f"{module_name}/dashboard.html", **context)


@module_blueprint.route("/check_pagecontent", methods=["GET", "POST"])
@login_required
@admin_required
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
        db.session.add(toaddpage)
        db.session.flush()
        toaddpage.insert_lang(form.lang.data, form.content.data)
        toaddpage.save()
        return redirect(url_for(f"{module_name}.dashboard"))


@module_blueprint.route("/edit_pagecontent", methods=["GET", "POST"])
@login_required
@admin_required
def edit_pagecontent():
    if request.method == "POST":
        form = PageForm()
        if not form.validate_on_submit():
            flash_errors(form)
            return redirect(url_for(f"{module_name}.dashboard"))

        editpage = db.session.query(Page).get(request.form["page_id"])
        editpage.slug = form.slug.data
        editpage.title = form.title.data
        editpage.content = form.content.data

        editpage.set_lang(form.lang.data, form.content.data)
        db.session.commit()
        return redirect(
            url_for(
                f"{module_name}.view_page_dashboard",
                slug=form.slug.data,
                lang=form.lang.data,
            )
        )
