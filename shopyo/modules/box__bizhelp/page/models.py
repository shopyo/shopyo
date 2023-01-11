from datetime import datetime

from flask import url_for
from init import db
from modules.box__bizhelp.i18n.models import LangRecord

from shopyo.api.models import PkModel


class Page(PkModel):

    __tablename__ = "pages"

    created_date = db.Column(db.DateTime, default=datetime.now())
    title = db.Column(db.String(100))
    slug = db.Column(db.String(100))

    def insert_lang(self, lang, content):
        record = LangRecord(strid=self.get_strid(), lang=lang, string=content)
        record.save(commit=False)

    def get_strid(self):
        return f"page_{self.slug}"

    def get_content(self, lang):
        page = Page.query.get(self.id)
        record = LangRecord.query.filter(
            LangRecord.strid == self.get_strid(), LangRecord.lang == lang
        ).first()
        if record is None:
            raise Exception("Record is None")

        return record.string

    def get_url(self, lang="en"):
        if self.slug:
            return url_for("page.view_page", slug=self.slug)
        else:
            return None

    def get_langs(self):
        records = LangRecord.query.filter(LangRecord.strid == self.get_strid()).all()

        page_langs = [p.lang for p in records]

        return page_langs
