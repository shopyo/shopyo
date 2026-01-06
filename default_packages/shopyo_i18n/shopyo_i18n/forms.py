from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class LanguageForm(FlaskForm):
    lang_code = StringField("Language Code", validators=[DataRequired()])
    lang_name = StringField("Language Name", validators=[DataRequired()])
