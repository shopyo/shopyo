from flask import Blueprint
from flask import render_template
from flask_login import login_required
from shopyo_auth.decorators import roles_required
from shopyo.api.module import ModuleHelp

mhelp = ModuleHelp(__file__, __name__)
globals()[mhelp.blueprint_str] = mhelp.blueprint
module_blueprint = globals()[mhelp.blueprint_str]

@module_blueprint.route("/")
@login_required
@roles_required("client") 
def index():
    """
    Only users with the 'client' role can access this view.
    """
    return "<h1>Welcome to the Client Portal</h1><p>Restricted access area.</p>"