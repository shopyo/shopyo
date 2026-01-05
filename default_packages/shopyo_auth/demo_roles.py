"""
Demo of Role-Based Access Control in Shopyo Auth
"""

from flask import Blueprint
from shopyo_auth.decorators import roles_required
from flask_login import login_required

# Create a demo blueprint
demo_blueprint = Blueprint("demo", __name__)

@demo_blueprint.route("/admin-only")
@login_required
@roles_required("admin")
def admin_only():
    """Only users with 'admin' role can access this."""
    return "Welcome, Admin!"

@demo_blueprint.route("/staff-access")
@login_required
@roles_required("admin", "staff")
def staff_access():
    """Users with either 'admin' or 'staff' role can access this."""
    return "Welcome, Staff Member!"

@demo_blueprint.route("/client-portal")
@login_required
@roles_required("client")
def client_portal():
    """Only users with 'client' role can access this."""
    return "Welcome to the Client Portal!"
