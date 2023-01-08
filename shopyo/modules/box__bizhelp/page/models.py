from datetime import datetime

from init import db
from modules.box__bizhelp.i18n.models import LangRecord

from shopyo.api.models import PkModel


class Page(PkModel):

    __tablename__ = "pages"

    created_date = db.Column(db.DateTime, default=datetime.now())
    title = db.Column(db.String(100))
    slug = db.Column(db.String(100))

    def insert_lang(lang, content):
        record = LangRecord(strid=f"page_{self.id}", lang=lang, string=content)

        record.save(commit=False)

    def get_strid():
        return f"page_"

    def get_content(lang):
        page = db.session.get(self.id)
        record = (
            db.session.query(LangRecord)
            .filter(LangRecord.strid == self.get_strid(), LangRecord.lang == lang)
            .first()
        )
        if record is None:
            raise Exception("Record is None")

        return record.string
