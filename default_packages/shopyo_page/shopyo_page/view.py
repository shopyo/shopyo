from flask import jsonify
from werkzeug.utils import secure_filename
import os
from flask import current_app
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

    form.content.data = page.get_content(lang=lang_arg)
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
            meta_description=form.meta_description.data,
            meta_keywords=form.meta_keywords.data,
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
        editpage.meta_description = form.meta_description.data
        editpage.meta_keywords = form.meta_keywords.data

        editpage.save_revision(
            form.lang.data,
            form.content.data,
            form.meta_description.data,
            form.meta_keywords.data,
        )

        editpage.set_lang(form.lang.data, form.content.data)
        db.session.commit()
        return redirect(
            url_for(
                f"{module_name}.view_page_dashboard",
                slug=form.slug.data,
                lang=form.lang.data,
            )
        )


@module_blueprint.route("/upload_image", methods=["POST"])
@login_required
@admin_required
def upload_image():
    if "file" in request.files:
        file = request.files["file"]
        if file:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(
                current_app.root_path, "static", "uploads", "images"
            )
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
            return jsonify({"location": f"/static/uploads/images/{filename}"})
    return jsonify({"error": "File not uploaded"}), 400


@module_blueprint.route("/dashboard/s/<slug>/revisions", methods=["GET"])
@login_required
@admin_required
def view_page_revisions(slug):
    context = {}
    page = Page.query.filter(Page.slug == slug).first()
    if page:
        context["page"] = page
        context["revisions"] = (
            PageRevision.query.filter_by(page_id=page.id)
            .order_by(PageRevision.revision_date.desc())
            .all()
        )
    return render_template(f"{module_name}/revisions.html", **context)


@module_blueprint.route("/revert/<int:revision_id>", methods=["POST"])
@login_required
@admin_required
def revert_page_revision(revision_id):
    revision = PageRevision.query.get(revision_id)
    if revision:
        page = Page.query.get(revision.page_id)
        if page:
            page.set_lang(revision.lang, revision.content)
            page.meta_description = revision.meta_description
            page.meta_keywords = revision.meta_keywords
            db.session.commit()
            flash("Page reverted successfully!", "success")
            return redirect(
                url_for(
                    f"{module_name}.view_page_dashboard",
                    slug=page.slug,
                    lang=revision.lang,
                )
            )
    flash("Error reverting page.", "danger")
    return redirect(url_for(f"{module_name}.dashboard"))
