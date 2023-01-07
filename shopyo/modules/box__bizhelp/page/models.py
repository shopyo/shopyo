from datetime import datetime

from shopyo.api.models import PkModel


class Page(PkModel):

    __tablename__ = "pages"
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=datetime.now())
    title = db.Column(db.String(100))
    slug = db.Column(db.String(100))
    content = db.Column(db.String(1024))
