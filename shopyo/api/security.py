from urllib.parse import urljoin
from urllib.parse import urlparse
import secrets
from flask import request, session, g

"""
Security utilities for Shopyo.

Includes:
- Safe URL redirection (`is_safe_redirect_url`, `get_safe_redirect`)
- CSRF token generation and validation (`generate_csrf_token`, `validate_csrf_token`)
- Jinja2 context processor helper (`inject_csrf_token`)

CSRF protection for form-based routes is handled globally by Flask-WTF's
``CSRFProtect`` (initialised in ``shopyo/init.py``). API clients can use
``generate_csrf_token`` and ``validate_csrf_token`` directly, or send the
token via the ``X-CSRFToken`` header or ``csrf_token`` form field.

The legacy ``csrf_protect`` decorator has been removed — it was redundant
with Flask-WTF's global protection.
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


def inject_csrf_token():
    """Inject CSRF token into Jinja2 template context.

    Returns
    -------
    dict
        Dictionary containing the CSRF token for template context.
    """
    return {CSRF_TOKEN_FORM_KEY: generate_csrf_token()}
