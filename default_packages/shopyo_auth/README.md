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
    - **Password Complexity**: Optional enforcement of strong passwords (uppercase, lowercase, digits, symbols).
    - **Brute-Force Protection**: Integrated `Flask-Limiter` for login and registration throttling.
    - **Safe Redirects**: Enforcement to prevent Open Redirect vulnerabilities.
    - **Case-Insensitive Lookups**: Prevents duplicate accounts via email variations.
    - **Secure Hashing**: Password hashing using Werkzeug's security helpers.
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
| `SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED` | Set to `True` to enforce strong password requirements (min 12 chars, upper, lower, digit, special). | `False` |
| `SHOPYO_AUTH_RATE_LIMIT_ENABLED` | Set to `True` to enable brute-force protection using Flask-Limiter. | `False` |
| `SHOPYO_AUTH_RATE_LIMIT` | The rate limit string (e.g., "5 per minute"). | `"5 per minute"` |

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

### 7. Rate Limiting

Rate limiting is powered by `Flask-Limiter`. To enable it, set `SHOPYO_AUTH_RATE_LIMIT_ENABLED` to `True` in your configuration. You can customize the limit using `SHOPYO_AUTH_RATE_LIMIT` (e.g., `"10 per minute"`).

```python
# The limiter instance is available for use in other blueprints if needed
from shopyo_auth import limiter

@module_blueprint.route("/heavy-op")
@limiter.limit("1 per second")
def heavy_op():
    return "Done!"
```

### 8. API Tokens (Personal Access Tokens)

Users can generate API tokens for programmatic access. These tokens are used via the `Authorization: Bearer <token>` header.

**Security Features:**
- **One-time Visibility**: Tokens are only shown once during creation.
- **Hashed Storage**: Only hashes of tokens are stored in the database.
- **Auto-Revocation**: Changing a password automatically revokes all active API tokens for that user.

**Protecting API Routes:**

```python
from shopyo_auth.decorators import token_required

@module_blueprint.route("/api/v1/resource")
@token_required
def api_resource():
    # g.current_user is populated with the authenticated user
    from flask import g
    return {"data": "secret", "user": g.current_user.email}
```

**Management Routes:**
- `GET /api/tokens`: List all active tokens.
- `POST /api/tokens`: Create a new token (expects `{"name": "my-token"}`).
- `DELETE /api/tokens/<id>`: Revoke a specific token.

### 9. Policy Engine (Granular Authorization)

The Policy Engine allows you to define complex, logic-based authorization rules that go beyond simple roles.

**Defining a Policy:**

```python
# In your app initialization or a blueprint
from shopyo_auth import ShopyoAuth

auth = ShopyoAuth(app)

def can_edit_user(user, **context):
    target_user_id = int(context.get("user_id"))
    return user.is_admin or user.id == target_user_id

auth.define_policy("edit_user", can_edit_user)
```

**Using the Policy:**

The `@require` decorator is a unified authorization tool that can check policies, roles, or admin status.

```python
from shopyo_auth.decorators import require

# Check a custom policy
@module_blueprint.route("/user/<int:user_id>/edit")
@require(policy="edit_user")
def edit_user(user_id):
    return "Editing user profile..."

# Check specific roles
@module_blueprint.route("/reports")
@require(roles=["manager", "admin"])
def view_reports():
    return "Reports data"

# Admin only
@module_blueprint.route("/system/config")
@require(admin_only=True)
def system_config():
    return "System configuration"
```

---
*Version 1.8.0*
