# Shopyo Auth

`shopyo_auth` is a robust authentication and user management package for the Shopyo ecosystem. It provides a complete, security-hardened foundation for handling users, roles, and session management.

[view docs for more info](https://shopyo.readthedocs.io/en/latest/)

## Description

This package implements a production-ready authentication system using Flask-Login and SQLAlchemy. It handles the entire lifecycle of a user account—from registration and email verification to secure login and role-based access control. Designed to be modular, it integrates seamlessly into Shopyo's plugin architecture while remaining flexible for customization.

## Features

- **Full Authentication Flow**: Pre-built views and forms for Login, Logout, and Registration.
- **Password Reset**: Secure, token-based password recovery workflow via email.
- **Flexible Role-Based Access Control (RBAC)**: Assign multiple roles to users and restrict access using granular decorators.
- **Email Confirmation**: Secure, token-based email verification system to validate new accounts.
- **Security Hardened**:
    - Case-insensitive email lookups to prevent duplicate accounts.
    - Safe redirect enforcement to prevent Open Redirect vulnerabilities.
    - Password hashing using Werkzeug's security helpers.
- **Configurable Verification**: Toggle email confirmation on or off via configuration settings.
- **Bootstrap-Ready Templates**: Includes clean, extensible templates that integrate with Shopyo's theme system.
- **Data Seeding**: Built-in utilities to bootstrap initial admin accounts and roles.

## How to Use

### 1. Initialization

In your Shopyo application factory, initialize the package:

```python
from shopyo_auth import ShopyoAuth

def create_app():
    app = Flask(__name__)
    # ... other setup ...
    auth = ShopyoAuth(app)
    return app
```

### 2. Configuration

You can customize the behavior of `shopyo_auth` using the following config variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SHOPYO_AUTH_URL` | The base URL prefix for all authentication routes. | `/shopyo-auth` |
| `EMAIL_CONFIRMATION_DISABLED` | Set to `True` to allow users to log in without verifying their email. | `False` |

### 3. Protecting Views

Use standard Flask-Login decorators or custom Shopyo Auth decorators to protect your routes:

```python
from flask_login import login_required
from shopyo_auth.decorators import check_confirmed, roles_required

# Requires login and email confirmation
@module_blueprint.route('/dashboard')
@login_required
@check_confirmed
def dashboard():
    return "Welcome to your verified dashboard!"

# Requires specific roles
@module_blueprint.route('/admin-panel')
@login_required
@roles_required('admin', 'editor')
def admin_panel():
    return "Welcome, privileged user!"
```

### 4. Role-Based Access Control (RBAC) Demo

Below is a demonstration of how to implement role-based access in your blueprints:

```python
from flask import Blueprint
from shopyo_auth.decorators import roles_required
from flask_login import login_required

demo_blueprint = Blueprint("demo", __name__)

@demo_blueprint.route("/staff-only")
@login_required
@roles_required("admin", "staff")
def staff_only():
    """Access allowed for users with 'admin' OR 'staff' roles."""
    return "Hello Staff!"

@demo_blueprint.route("/admin-only")
@login_required
@roles_required("admin")
def admin_only():
    """Access restricted to users with the 'admin' role only."""
    return "Hello Admin!"
```

### 5. Resetting Passwords

The password reset workflow is handled automatically via the `/forgot-password` and `/reset-password/<token>` routes. Users can request a reset link by providing their email address. If the account exists, an email is sent with a secure, timed link to set a new password.

### 6. Seeding Admin Users

To bootstrap your application with a default admin user, you can use the built-in seeding utility:

```python
from shopyo_auth import upload

# This will read from your config.json and create the admin user
upload()
```

---
*Version 1.2.0*
