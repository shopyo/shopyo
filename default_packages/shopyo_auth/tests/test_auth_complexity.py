import pytest
from wtforms.validators import ValidationError
from shopyo_auth.forms import PasswordComplexity, RegistrationForm
from flask import Flask


def test_password_complexity_validator(flask_app):
    validator = PasswordComplexity()

    class Field:
        def __init__(self, data):
            self.data = data

    with flask_app.app_context():
        # Case 1: Disabled (Backward Compatible)
        flask_app.config["SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED"] = False
        # Simple password should pass
        validator(None, Field("pass"))

        # Case 2: Enabled
        flask_app.config["SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED"] = True

        # Valid password
        validator(None, Field("Pass1234!@#$"))

        # Short password (min 12)
        with pytest.raises(ValidationError) as excinfo:
            validator(None, Field("Pass1!"))
        assert "at least 12 characters" in str(excinfo.value)

        # Missing uppercase
        with pytest.raises(ValidationError):
            validator(None, Field("pass1234!@#$"))

        # Missing lowercase
        with pytest.raises(ValidationError):
            validator(None, Field("PASS1234!@#$"))

        # Missing digit
        with pytest.raises(ValidationError):
            validator(None, Field("Pass!!!!@#$"))

        # Missing special character
        with pytest.raises(ValidationError):
            validator(None, Field("Pass12345678"))


def test_registration_form_complexity(flask_app):
    with flask_app.test_request_context():
        # Case 1: Disabled
        flask_app.config["SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED"] = False
        form = RegistrationForm(
            email="test@example.com", password="password", confirm="password"
        )
        assert form.validate() is True

        # Case 2: Enabled
        flask_app.config["SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED"] = True
        # Test valid
        form = RegistrationForm(
            email="test@example.com", password="Pass1234!@#$", confirm="Pass1234!@#$"
        )
        assert form.validate() is True

        # Test missing complexity
        form = RegistrationForm(
            email="test@example.com", password="password12345", confirm="password12345"
        )
        assert form.validate() is False
        assert (
            "Password must contain at least one uppercase letter"
            in form.password.errors[0]
        )
