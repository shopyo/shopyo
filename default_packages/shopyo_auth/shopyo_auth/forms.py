import re

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import InputRequired
from wtforms.validators import Length
from wtforms.validators import ValidationError


class PasswordComplexity:
    """
    Validator to check for password complexity.
    Requires at least one uppercase, one lowercase, one digit, and one special character.
    If SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED is False, it passes.
    """

    def __init__(self, message=None):
        if not message:
            message = (
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character."
            )
        self.message = message

    def __call__(self, form, field):
        if not current_app.config.get("SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED", False):
            return

        password = field.data
        if len(password) < 12:
            raise ValidationError(
                "Password must be at least 12 characters when complexity is enabled."
            )

        if not re.search(r"[A-Z]", password):
            raise ValidationError(self.message)
        if not re.search(r"[a-z]", password):
            raise ValidationError(self.message)
        if not re.search(r"\d", password):
            raise ValidationError(self.message)
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError(self.message)


class LoginForm(FlaskForm):
    email = EmailField(
        "email",
        [DataRequired(), Email(message="Not a valid email address.")],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    password = PasswordField(
        "Password",
        [DataRequired()],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )


class RegistrationForm(FlaskForm):
    """Registration Form"""

    email = EmailField(
        "email_label",
        [DataRequired(), Email(message="Not a valid email address.")],
    )

    password = PasswordField(
        "New Password",
        validators=[
            InputRequired("Password is required"),
            Length(
                min=6,
                max=128,
                message="Password must be between 6 and 128 characters",
            ),
            PasswordComplexity(),
            EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField(
        "Repeat Password",
    )

    def validate_email(self, field):
        """
        Inline validator for email. Checks to see if a user object with
        entered email already present in the database

        Args:
            field : The form field that contains email data.

        Raises:
            ValidationError: if the username entered in the field is already
            in the database
        """
        try:
            from .models import User
        except Exception as e:
            raise e
        user = User.get_by_email(field.data)

        if user is not None:
            raise ValidationError(f"email '{field.data}' is already in use.")


class ForgotPasswordForm(FlaskForm):
    email = EmailField(
        "Email",
        [DataRequired(), Email(message="Not a valid email address.")],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[
            InputRequired("Password is required"),
            Length(
                min=6,
                max=128,
                message="Password must be between 6 and 128 characters",
            ),
            PasswordComplexity(),
            EqualTo("confirm", message="Passwords must match"),
        ],
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
    confirm = PasswordField(
        "Repeat Password",
        render_kw={"class": "form-control", "autocomplete": "off"},
    )
