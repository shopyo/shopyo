from datetime import datetime

from init import db

from shopyo.api.models import PkModel


class LangString(PkModel):
    __tablename__ = "i18n_strings"
    lang = db.Column(db.String(10))
    string = db.Column(db.Text())

    record_id = db.Column(db.Integer, db.ForeignKey("i18n_records.id"))


class LangRecord(PkModel):
    __tablename__ = "i18n_records"
    strid = db.Column(db.String(1024))
    strings = db.relationship("LangString", backref="record")
