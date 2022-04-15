from urllib.parse import urljoin
from urllib.parse import urlparse

from flask import request


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
