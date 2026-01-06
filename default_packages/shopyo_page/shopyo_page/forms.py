from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from shopyo_i18n.models import LangRecord

from shopyo.api.validators import verify_slug


class PageForm(FlaskForm):
    content = TextAreaField(
        "Content",
        [],
        render_kw={
            "class": "form-control",
            "rows": "20",
            "autocomplete": "off",
        },
    )
    slug = StringField(
        "Slug",
        [DataRequired(), verify_slug],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    title = StringField(
        "Title",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    meta_description = StringField(
        "Meta Description",
        [],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    meta_keywords = StringField(
        "Meta Keywords",
        [],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    lang = SelectField("Language")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lang.choices = [(l.lang_code, l.lang_name) for l in LangRecord.query.all()]
