Policy Engine Tutorial
======================

The Policy Engine (``shopyo.api.perms``) provides a structured authorization
system that replaces ad-hoc ``is_admin`` checks with typed permissions,
role-based grants, and custom policy functions.

Motivation
----------

Before the policy engine, admin access was gated by a simple boolean:

.. code-block:: python

    if current_user.is_admin:
        # grant access

This approach breaks down as your app grows:

* You need multiple privilege levels (moderator, editor, admin)
* Permissions should be granular (``USER_READ`` vs ``USER_MANAGE``)
* Authorization rules often depend on the resource (user can edit own post)
* Testing auth logic requires mocking database columns

The Policy Engine solves all of these.

Core Concepts
-------------

**Permission**
  A named enum member representing a single action. Eight built-in
  permissions cover common needs:

  .. list-table::
     :header-rows: 1

     * - Permission
       - Typical Use
     * - ``Permission.ADMIN_PANEL_ACCESS``
       - Enter the admin dashboard and navigation
     * - ``Permission.USER_MANAGE``
       - Create, read, update, delete users
     * - ``Permission.USER_READ``
       - View user profiles and listing
     * - ``Permission.ROLE_MANAGE``
       - Create and assign roles
     * - ``Permission.SETTINGS_MANAGE``
       - Modify application settings
     * - ``Permission.CONTENT_MANAGE``
       - Create, edit, delete content
     * - ``Permission.CONTENT_PUBLISH``
       - Publish or approve content
     * - ``Permission.DASHBOARD_VIEW``
       - View analytics dashboard

**Policy**
  A dataclass wrapping a name and a callable ``check(user, resource) -> bool``.
  Custom policies let you implement resource-aware rules.

**PolicyEngine**
  The main entry point. It manages role-permission mappings and
  custom policies, and provides the ``@require()`` decorator for views.

Engine Setup
------------

Create a global engine instance, typically in your app factory:

.. code-block:: python

    from shopyo.api.perms import PolicyEngine, Permission

    engine = PolicyEngine()

    # Grant permissions to roles
    engine.grant("admin", Permission.ADMIN_PANEL_ACCESS, Permission.USER_MANAGE,
                          Permission.ROLE_MANAGE, Permission.SETTINGS_MANAGE)
    engine.grant("editor", Permission.CONTENT_MANAGE, Permission.CONTENT_PUBLISH)
    engine.grant("viewer", Permission.DASHBOARD_VIEW)

Role-Based Access (RBAC)
------------------------

Map permissions to roles at startup. Users inherit permissions through
their assigned roles:

.. code-block:: python

    from flask import g
    from flask_login import current_user

    # View protected by role-based permission
    @engine.require(Permission.ADMIN_PANEL_ACCESS)
    def admin_panel():
        return render_template("admin/dashboard.html")

    # Multiple checks compose naturally
    @engine.require(Permission.USER_MANAGE)
    def user_list():
        users = User.query.all()
        return render_template("admin/users.html", users=users)

The ``require`` decorator:

* Returns **401** if the user is not authenticated
* Returns **403** if the user lacks the required permission
* Calls the view function otherwise

Legacy admin users (``is_admin=True``) still pass all permission checks
during the transitional period — no code changes needed for existing admins.

Assigning Roles to Users
------------------------

The Policy Engine knows which permissions a role carries, but you must
assign roles to users in the database. The ``User`` model has a
many-to-many relationship with ``Role``:

.. code-block:: python

    from shopyo_auth.models import User, Role
    from init import db

    # Create a role in the database
    moderator_role = Role.create(name="moderator")
    db.session.commit()

    # Assign the role to a user
    user = User.get_by_email("alice@example.com")
    user.roles.append(moderator_role)
    user.save()

    # Assign multiple roles at once
    admin_role = Role.create(name="admin")
    editor_role = Role.create(name="editor")
    user.roles = [admin_role, editor_role]
    user.save()

**Important:** Creating a role in the database and granting permissions to
that role name in the Policy Engine are two separate steps:

+------------------------------------+---------------------------------------+
| Step                               | Where                                 |
+====================================+=======================================+
| ``Role.create(name="mod")``        | Database — creates the role record    |
+------------------------------------+---------------------------------------+
| ``engine.grant("mod", ...)``       | Code — maps role name to permissions  |
+------------------------------------+---------------------------------------+
| ``user.roles.append(mod_role)``    | Database — assigns role to user       |
+------------------------------------+---------------------------------------+

All three are required for role-based access to work:

.. code-block:: python

    # 1. Database: create the role record
    mod_role = Role.create(name="moderator")

    # 2. Code: tell the PolicyEngine what "moderator" means
    engine.grant("moderator", Permission.CONTENT_MANAGE, Permission.DASHBOARD_VIEW)

    # 3. Database: assign the role to the user
    user.roles.append(mod_role)
    user.save()

    # Now this check passes:
    engine.has_permission(user, Permission.CONTENT_MANAGE)  # True

You can also check which roles a user has at runtime:

.. code-block:: python

    role_names = [r.name for r in user.roles]
    if "admin" in role_names:
        # custom logic

Resource-Specific Policies
--------------------------

When access depends on *which* resource is being accessed, define a custom
policy:

.. code-block:: python

    # Only allow users to edit their own profiles
    engine.define(
        "perm.USER_MANAGE",
        lambda user, resource: user.is_admin or user.id == resource.id
    )

    @engine.require(Permission.USER_MANAGE, resource=some_user)
    def edit_user(some_user):
        ...

The ``resource`` argument is forwarded to the policy check callable.
A policy named ``perm.<PERMISSION_NAME>`` is automatically looked up when
no role grant matches.

Combining Roles and Policies
----------------------------

The ``has_permission`` check follows this order:

#. If ``user.is_admin`` is ``True`` → grant access (transitional)
#. If any of the user's roles have the permission → grant access
#. If a policy named ``perm.<PERMISSION_NAME>`` is defined → delegate to it
#. Otherwise → deny access

This means role grants take precedence over policies, which is useful for
overriding a restrictive default:

.. code-block:: python

    # Default: nobody can delete content
    engine.define("perm.CONTENT_MANAGE", lambda user, resource: False)

    # Except admins
    engine.grant("admin", Permission.CONTENT_MANAGE)

Full Example
------------

.. code-block:: python

    from shopyo.api.perms import PolicyEngine, Permission

    engine = PolicyEngine()

    # --- Setup grants ---
    engine.grant("admin", Permission.ADMIN_PANEL_ACCESS,
                          Permission.USER_MANAGE,
                          Permission.ROLE_MANAGE)
    engine.grant("editor", Permission.CONTENT_MANAGE)

    # --- Custom policy: author can edit own article ---
    engine.define(
        "perm.CONTENT_MANAGE",
        lambda user, resource: resource is not None and resource.author_id == user.id
    )

    # --- In views ---
    @app.route("/admin")
    @engine.require(Permission.ADMIN_PANEL_ACCESS)
    def admin_index():
        return "Admin area"

    @app.route("/articles/<int:article_id>/edit")
    @engine.require(Permission.CONTENT_MANAGE, resource=article)
    def edit_article(article_id):
        article = Article.query.get_or_404(article_id)
        # ...

    # --- Programmatic check ---
    if engine.has_permission(current_user, Permission.USER_MANAGE):
        show_admin_controls()

Migration from ``is_admin``
---------------------------

Replace direct ``is_admin`` checks with equivalent permission checks:

+---------------------------------------------+------------------------------------------------------------------------+
| Before                                      | After                                                                  |
+=============================================+========================================================================+
| ``current_user.is_admin``                   | ``engine.has_permission(current_user, Permission.ADMIN_PANEL_ACCESS)`` |
+---------------------------------------------+------------------------------------------------------------------------+
| ``@admin_required``                         | ``@engine.require(Permission.ADMIN_PANEL_ACCESS)``                     |
+---------------------------------------------+------------------------------------------------------------------------+
| ``@require(admin_only=True)``               | ``@engine.require(Permission.ADMIN_PANEL_ACCESS)``                     |
+---------------------------------------------+------------------------------------------------------------------------+
| ``@roles_required("admin")``                | ``engine.grant("admin", Perm.ADMIN_PANEL_ACCESS)``                     |
|                                             | ``@engine.require(Permission.ADMIN_PANEL_ACCESS)``                     |
+---------------------------------------------+------------------------------------------------------------------------+

Testing Policies
----------------

Since the PolicyEngine is framework-agnostic, you can unit test it
without setting up Flask:

.. code-block:: python

    from unittest.mock import Mock
    from shopyo.api.perms import PolicyEngine, Permission

    def test_admin_bypasses_all_checks():
        engine = PolicyEngine()
        admin = Mock(is_admin=True, roles=[])
        assert engine.has_permission(admin, Permission.ADMIN_PANEL_ACCESS)
        assert engine.has_permission(admin, Permission.USER_MANAGE)

    def test_role_based_access():
        engine = PolicyEngine()
        engine.grant("admin", Permission.USER_MANAGE)
        role = Mock(name="admin")
        role.name = "admin"
        user = Mock(is_admin=False, roles=[role])
        assert engine.has_permission(user, Permission.USER_MANAGE)
        assert not engine.has_permission(user, Permission.SETTINGS_MANAGE)

    def test_custom_policy_with_resource():
        engine = PolicyEngine()
        engine.define(
            "perm.CONTENT_MANAGE",
            lambda user, resource: resource.owner_id == user.id
        )
        user = Mock(is_admin=False, roles=[], id=1)
        doc = Mock(owner_id=1)
        assert engine.has_permission(user, Permission.CONTENT_MANAGE, resource=doc)

Reference
---------

For the complete API reference see :doc:`shopyoapi`.
