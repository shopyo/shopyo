from flask import current_app

from init import db
from shopyo_settings.models import Settings


def add_setting(name, value):
    if Settings.query.filter_by(setting=name).first():
        s = Settings.query.get(name)
        s.value = value
        db.session.commit()
    else:
        s = Settings(setting=name, value=value)
        db.session.add(s)
        db.session.commit()


def upload(verbose=False):
    for name, value in current_app.config["SEED_SETTINGS"].items():
        add_setting(name, value)
        print("Uploading settings to db:", name, value)

    if verbose:
        print("[x] Added Dummy Settings")
