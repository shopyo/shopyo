import json
import os

from flask import current_app
from flask import url_for


def base_context():
    """
    Used to define global template values


    Returns
    -------
    dict
        copy of dictionary
    """

    base_context = {}
    return base_context.copy()
