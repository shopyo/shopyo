How to Add Auth to Flask Without Going Insane
==============================================

.. post:: 2026-05-28
   :tags: flask, auth, authentication, security, tutorial
   :category: Tutorial
   :author: Shopyo Team

Authentication is the most-reimplemented feature in the Flask ecosystem. Every Flask developer has written a login system at least once. Most have written it three or four times, across different projects, with slightly different bugs each time.

This post walks through what a production-grade auth system needs — and how to get it without building it from scratch.

The Minimum Viable Auth Stack
-----------------------------

A production-ready auth system needs:

- **User registration** with email verification
- **Login/logout** with session management
- **Password reset** with secure tokens
- **Password complexity** enforcement (length, character classes)
- **Rate limiting** on login and registration endpoints
- **CSRF protection** on all forms
- **API token authentication** for programmatic access
- **Role-based access control** for permissions
- **Session hardening** (HttpOnly, SameSite, Secure cookies)

Let's look at what it takes to build this from scratch.

Building Auth with Flask Extensions
-----------------------------------

The standard approach is wiring together several extensions:

.. code-block:: bash

   pip install flask-login flask-wtf itsdangerous bcrypt email-validator

Then implementing models, forms, views, email-sending, token generation, and rate limiting manually. For a typical app, this is **300-500 lines of code** spread across 6-8 files. And you still need to:

- Write email templates for verification and password reset
- Implement rate limiting with Flask-Limiter
- Add password complexity validation
- Secure session cookies in `config.py`
- Write the HTML templates for login, register, password reset
- Handle edge cases (expired tokens, already-verified users, brute force attempts)

Most Flask auth implementations have at least one of these common bugs:

- Timing-attack-vulnerable token comparison
- Session fixation
- No account lockout
- Logging passwords in error messages
- Missing CSRF on login forms
- Predictable password reset tokens

The Shopyo Approach
-------------------

Shopyo's auth module (``shopyo_auth``) gives you all of the above in one install:

.. code-block:: bash

   pip install shopyo
   shopyo new myapp
   cd myapp && shopyo initialise && flask run

This gives you a working auth system at ``/auth/login``, ``/auth/register``, ``/auth/reset-password`` — with all of the following built in:

.. list-table::
   :header-rows: 1

   * - Feature
     - Status
   * - Email/password registration
     - ✅
   * - Email verification
     - ✅
   * - Password reset flow
     - ✅
   * - Password complexity (min 12 chars, mixed case, digits, symbols)
     - ✅ (default)
   * - Rate limiting (per-endpoint)
     - ✅ (default)
   * - Session cookies (HttpOnly, SameSite=Lax, Secure in prod)
     - ✅
   * - CSRF protection
     - ✅ (global)
   * - API token auth (PBKDF2-HMAC hashed)
     - ✅
   * - Role-based permissions
     - ✅ (policy engine)
   * - Persistent "remember me"
     - ✅
   * - Custom login/register templates
     - ✅

You also get the full test suite — the auth module has 11 test files covering models, forms, roles, tokens, rate limiting, policy, events, and password complexity.

Configuring Auth
----------------

Auth behavior is controlled by environment variables and config keys:

.. code-block:: python

   # config.py
   SHOPYO_AUTH_RATE_LIMIT_LOGIN = "5 per minute"
   SHOPYO_AUTH_RATE_LIMIT_REGISTER = "2 per hour"
   SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED = True
   SHOPYO_AUTH_MIN_PASSWORD_LENGTH = 12
   SHOPYO_AUTH_SEED_ADMIN_EMAIL = "admin@example.com"
   SHOPYO_AUTH_SEED_ADMIN_PASSWORD = None  # must be set via env

The setup is intentionally secure-by-default. Rate limiting and password complexity are enabled out of the box. Hardcoded secret defaults are removed in v5 — everything comes from environment variables in production.

Why This Matters
----------------

Authentication is not a differentiator for your product. It's table stakes. Every hour you spend debugging password reset tokens is an hour you're not building features your users actually care about.

Using a pre-built auth system isn't "lazy" — it's the responsible choice. The auth module in Shopyo has been tested across multiple Python versions (3.7–3.13), operating systems (Linux, macOS, Windows), and production deployments (Maurilearn.com, FlaskCon.com). It has 71%+ test coverage, a security policy, and active maintenance.

Next Steps for Shopyo Auth
---------------------------

- :doc:`/auth_tutorial` — Deep dive into Shopyo's auth system
- :doc:`/policy_tutorial` — Role-based access control with the policy engine
- :doc:`/quickstart` — Get Shopyo running in 10 minutes
