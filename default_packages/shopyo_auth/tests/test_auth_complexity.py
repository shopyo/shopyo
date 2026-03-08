"""
Elite Unit Tests for Password Complexity.
Uses parametrization to enforce strict security boundaries.
"""

import pytest
from wtforms.validators import ValidationError
from werkzeug.datastructures import MultiDict
from shopyo_auth.forms import PasswordComplexity, RegistrationForm


class TestPasswordComplexity:
    """Tests for the core complexity validator logic."""

    @pytest.mark.parametrize(
        "password",
        [
            "Pass1234!@#$",
            "Stronger_1234!",
            "Valid8_Token$",
        ],
    )
    def test_valid_passwords(self, password, flask_app):
        """Verify that compliant passwords pass without error."""
        validator = PasswordComplexity()

        class Field:
            data = password

        with flask_app.app_context():
            flask_app.config["SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED"] = True
            # Should not raise
            validator(None, Field())

    @pytest.mark.parametrize(
        "password, error_match",
        [
            ("pass", "at least 12 characters"),
            ("pass1234!@#$", "uppercase letter"),
            ("PASS1234!@#$", "lowercase letter"),
            ("Pass!!!!@#$%", "one digit"),
            ("Pass12345678", "special character"),
        ],
    )
    def test_invalid_passwords(self, password, error_match, flask_app):
        """Verify that non-compliant passwords trigger specific errors."""
        validator = PasswordComplexity()

        class Field:
            data = password

        with flask_app.app_context():
            flask_app.config["SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED"] = True
            with pytest.raises(ValidationError, match=error_match):
                validator(None, Field())

    def test_disabled_complexity(self, flask_app):
        """Verify backward compatibility: simple passwords pass when disabled."""
        validator = PasswordComplexity()

        class Field:
            data = "simple"

        with flask_app.app_context():
            flask_app.config["SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED"] = False
            # Should pass despite being non-compliant
            validator(None, Field())


class TestRegistrationFormIntegration:
    """Integration tests for forms using the complexity validator."""

    def test_form_validation_enabled(self, flask_app):
        """Verify form rejects simple password when complexity is enabled."""
        with flask_app.test_request_context():
            flask_app.config["SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED"] = True

            data = MultiDict(
                {"email": "test@example.com", "password": "simple", "confirm": "simple"}
            )
            form = RegistrationForm(data)
            assert form.validate() is False
            assert any("at least 12 characters" in err for err in form.password.errors)

    def test_form_validation_disabled(self, flask_app):
        """Verify form accepts simple password when complexity is disabled."""
        with flask_app.test_request_context():
            flask_app.config["SHOPYO_AUTH_PASSWORD_COMPLEXITY_ENABLED"] = False

            data = MultiDict(
                {
                    "email": "test@example.com",
                    "password": "password",
                    "confirm": "password",
                }
            )
            form = RegistrationForm(data)
            # Length 6 is still enforced by WTForms Length validator
            assert form.validate() is True
