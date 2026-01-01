from urllib.parse import urljoin
from urllib.parse import urlparse
from functools import wraps
import secrets
from flask import request, session, abort, g

"""
Security utilities for Shopyo.

Includes:
- Safe URL redirection (`is_safe_redirect_url`, `get_safe_redirect`)
- CSRF protection: token generation, validation, and decorator for Flask views
  (`generate_csrf_token`, `validate_csrf_token`, `get_csrf_token_from_request`, `csrf_protect`)
- Jinja2 context processor helper (`inject_csrf_token`)
"""


# from https://security.openstack.org/guidelines/dg_avoid-unvalidated-redirects.html
def is_safe_redirect_url(target):
    """
    Corresponds to Djangos is_safe_url


    Args:
        target (String): url

    Returns
    -------
    bool
    """
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return (
        redirect_url.scheme in ("http", "https")
        and host_url.netloc == redirect_url.netloc
    )


def get_safe_redirect(url):
    """
    Returns url for root path if url not safe


    Args:
        url (String): url

    Returns
    -------
    url or root page
    """

    if url and is_safe_redirect_url(url):
        return url

    url = request.referrer
    if url and is_safe_redirect_url(url):
        return url

    return "/"


CSRF_TOKEN_SESSION_KEY = "_csrf_token"
CSRF_TOKEN_HEADER = "X-CSRFToken"
CSRF_TOKEN_FORM_KEY = "csrf_token"


def generate_csrf_token():
    """Generate a secure CSRF token.

    Generates a secure CSRF token and stores it in the session if not present.

    Returns
    -------
    str
        The generated CSRF token.
    """
    token = session.get(CSRF_TOKEN_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(64)
        session[CSRF_TOKEN_SESSION_KEY] = token
    return token


def validate_csrf_token(token):
    """Validate the CSRF token using constant-time comparison.

    Parameters
    ----------
    token : str
        The CSRF token to validate.

    Returns
    -------
    bool
        True if the token is valid, False otherwise.
    """
    session_token = session.get(CSRF_TOKEN_SESSION_KEY)
    if not session_token or not token:
        return False
    # Constant-time comparison to prevent timing attacks
    return secrets.compare_digest(session_token, token)


def get_csrf_token_from_request():
    """Extract CSRF token from request.

    Tries to extract CSRF token from headers, form, or JSON in that order.

    Returns
    -------
    str or None
        The CSRF token if found, None otherwise.
    """
    # 1. Check header
    token = request.headers.get(CSRF_TOKEN_HEADER)
    if token:
        return token
    # 2. Check form
    token = request.form.get(CSRF_TOKEN_FORM_KEY)
    if token:
        return token
    # 3. Check JSON
    if request.is_json:
        json_data = request.get_json(silent=True)
        if json_data and CSRF_TOKEN_FORM_KEY in json_data:
            return json_data[CSRF_TOKEN_FORM_KEY]
    return None


def csrf_protect(view_func):
    """Decorator to protect endpoints against CSRF attacks.

    Checks for a valid CSRF token in header, form, or JSON for unsafe methods
    (POST, PUT, PATCH, DELETE).

    Parameters
    ----------
    view_func : function
        The view function to protect.

    Returns
    -------
    function
        The wrapped view function with CSRF protection.

    Raises
    ------
    werkzeug.exceptions.Forbidden
        If CSRF token is missing or invalid.
    """

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        # Only protect unsafe methods
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            token = get_csrf_token_from_request()
            if not validate_csrf_token(token):
                abort(403, description="CSRF token missing or invalid.")
        return view_func(*args, **kwargs)

    return wrapped_view


def inject_csrf_token():
    """Inject CSRF token into Jinja2 template context.

    Returns
    -------
    dict
        Dictionary containing the CSRF token for template context.
    """
    return {CSRF_TOKEN_FORM_KEY: generate_csrf_token()}
