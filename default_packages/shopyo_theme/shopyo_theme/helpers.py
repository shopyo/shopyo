import json
import os

from flask import current_app
from flask import url_for
from init import themes_path
from shopyo_settings.helpers import get_setting


def _get_blueprint_theme_dir(theme_name):
    parts = theme_name.split("/", 1)
    if len(parts) == 2:
        bp_name, local_name = parts
    else:
        return None
    bp = current_app.blueprints.get(bp_name)
    if bp is None:
        return None
    for kind in ("back", "front"):
        candidate = os.path.join(bp.root_path, "static", "themes", kind, local_name)
        if os.path.isdir(candidate):
            return candidate
    return None


def get_front_theme_dir():
    active_theme = (
        current_app.config["SHOPYO_THEME_FRONT_DEFAULT"]
        or current_app.config["SHOPYO_THEME_DEFAULT"]
        or get_setting("ACTIVE_FRONT_THEME")
    )
    bp_dir = _get_blueprint_theme_dir(active_theme)
    if bp_dir:
        return bp_dir
    theme_dir = os.path.join(themes_path, "front", active_theme)
    return theme_dir


def get_front_theme_info_data():
    info_path = os.path.join(get_front_theme_dir(), "info.json")
    with open(info_path) as f:
        info_data = json.load(f)
    return info_data


def get_active_front_theme():
    return (
        current_app.config["SHOPYO_THEME_FRONT_DEFAULT"]
        or current_app.config["SHOPYO_THEME_DEFAULT"]
        or get_setting("ACTIVE_FRONT_THEME")
    )


def get_active_front_theme_version():
    return get_front_theme_info_data()["version"]


def get_active_front_theme_styles_url():
    active_theme = get_active_front_theme()
    if "/" in active_theme:
        bp_name = active_theme.split("/", 1)[0]
        filename = f"themes/front/{active_theme.split('/', 1)[1]}/styles.css"
        return url_for(f"{bp_name}.static", filename=filename)
    return url_for(
        "shopyo_theme.active_front_theme_css",
        active_theme=active_theme,
        v=get_active_front_theme_version(),
    )


def get_back_theme_dir():
    active_theme = current_app.config["SHOPYO_THEME_BACK_DEFAULT"] or get_setting(
        "ACTIVE_BACK_THEME"
    )
    bp_dir = _get_blueprint_theme_dir(active_theme)
    if bp_dir:
        return bp_dir
    theme_dir = os.path.join(themes_path, "back", active_theme)
    return theme_dir


def get_back_theme_info_data():
    info_path = os.path.join(get_back_theme_dir(), "info.json")
    with open(info_path) as f:
        info_data = json.load(f)
    return info_data


def get_active_back_theme():
    return current_app.config["SHOPYO_THEME_BACK_DEFAULT"] or get_setting(
        "ACTIVE_BACK_THEME"
    )


def get_active_back_theme_version():
    return get_back_theme_info_data()["version"]


def get_active_back_theme_styles_url():
    active_theme = get_active_back_theme()
    if "/" in active_theme:
        bp_name = active_theme.split("/", 1)[0]
        filename = f"themes/back/{active_theme.split('/', 1)[1]}/styles.css"
        return url_for(f"{bp_name}.static", filename=filename)
    return url_for(
        "shopyo_theme.active_back_theme_css",
        active_theme=active_theme,
        v=get_active_back_theme_version(),
    )
