from flask import session


def get_current_lang():
    return session.get("yo_current_language", "en")


def get_default_lang():
    return session.get("yo_default_language", "en")
