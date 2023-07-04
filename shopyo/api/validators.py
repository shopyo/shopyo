import os
import re

from wtforms.validators import ValidationError

# https://wtforms.readthedocs.io/en/2.3.x/validators/


def get_module_path_if_exists(name):
    root_path = os.getcwd()

    for folder in os.listdir(os.path.join(root_path, "modules")):
        module_path = os.path.join(root_path, "modules", folder)
        sub_module_path = os.path.join(module_path, name)

        if folder == name:
            return module_path

        if os.path.exists(sub_module_path):
            return sub_module_path

    return None


def is_alpha_num_underscore(name):
    """returns whether the given name contains only alphanumeric or underscore

    Parameters
    ----------
    name : str
        to value to check for alphanumeric or underscore

    Returns
    -------
    bool
        returns ``True`` if ``name`` is alphanumeric, ``False`` otherwise
    """
    return bool(re.match(r"^[A-Za-z0-9_]+$", name))


def is_empty_str(string):
    return string.strip() == ""


def is_valid_slug(text):
    # from validators package
    slug_regex = re.compile(r"^[-a-zA-Z0-9_]+$")
    return slug_regex.match(text)


def is_valid_url(url):
    protocol = r"^((?:http|ftp)s?://)?"
    domain = r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|localhost)"
    ipv4 = r"(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}"
    ipv6 = r"([a-f0-9:]+:+)+[a-f0-9]+"
    port = r"(?::\d+)?(?:/?|[/?]\S+)$"
    url_regex = re.compile(
        protocol + domain + "|" + ipv4 + "|" + ipv6 + port, re.IGNORECASE
    )
    return url_regex.match(url) is not None


def verify_slug(form, field):
    if not is_valid_slug(field.data):
        raise ValidationError(
            "Slugs can only contain alphabets, numbers and hyphens (-). eg. good-day-1"
        )
