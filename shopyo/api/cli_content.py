import textwrap


def get_module_view_content():
    content = textwrap.dedent(
        """\
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
    )

    return content


def get_dashboard_html_content():
    content = textwrap.dedent(
        """\
        {% extends "base/module_base.html" %}
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
    )

    return content


def get_global_py_content():
    content = textwrap.dedent(
        """\
        available_everywhere = {

        }
        """
    )

    return content
