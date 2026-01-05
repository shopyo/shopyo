from init import db
from shopyo.api.models import PkModel


class Question(PkModel):
    __tablename__ = "questions"
    text = db.Column(db.String(200), nullable=False)
    options = db.relationship(
        "Option", backref="question", lazy=True, cascade="all, delete-orphan"
    )


class Option(PkModel):
    __tablename__ = "options"
    text = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
