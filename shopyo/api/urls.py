"""
.. module:: urls
    :synopsis: Helpers to build absolute URLs for outbound links.
"""

from flask import current_app
from flask import url_for


def absolute_url(endpoint, **values):
    """Build an absolute URL for ``endpoint``.

    Outbound links (e.g. in password-reset or confirmation emails) must
    not inherit the request Host header, which a client controls: a
    poisoned Host would put attacker-controlled links into the email.

    - If ``APP_URL`` is configured (e.g. ``https://example.com``), it is
      used as the base.
    - Otherwise falls back to ``url_for(_external=True)``, which honours
      ``SERVER_NAME`` when set and the request host otherwise (dev
      convenience).
    """
    base = current_app.config.get("APP_URL")
    if base:
        return base.rstrip("/") + url_for(endpoint, **values)
    return url_for(endpoint, _external=True, **values)
