import pytest
from flask import Flask
from unittest.mock import MagicMock, patch
from shopyo.api.email import send_async_email, _send_email_helper


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["MAIL_DEFAULT_SENDER"] = "test@example.com"
    app.config["MAIL_USERNAME"] = "user"
    app.config["MAIL_PASSWORD"] = "pass"
    return app


def test_send_async_email(app):
    with app.test_request_context():
        with patch("shopyo.api.email.render_template", return_value="content"):
            with patch("shopyo.api.email.EmailMultiAlternatives") as mock_email_class:
                mock_msg = MagicMock()
                mock_email_class.return_value = mock_msg
                with patch("shopyo.api.email.Thread") as mock_thread_class:
                    mock_thread = MagicMock()
                    mock_thread_class.return_value = mock_thread

                    send_async_email("to@example.com", "Subject", "template")

                    assert mock_email_class.called
                    assert mock_thread_class.called
                    assert mock_thread.start.called


def test_send_async_email_with_custom_sender(app):
    with app.test_request_context():
        with patch("shopyo.api.email.render_template", return_value="content"):
            with patch("shopyo.api.email.EmailMultiAlternatives") as mock_email_class:
                mock_msg = MagicMock()
                mock_email_class.return_value = mock_msg
                with patch("shopyo.api.email.Thread") as mock_thread_class:
                    mock_thread = MagicMock()
                    mock_thread_class.return_value = mock_thread

                    send_async_email(
                        "to@example.com",
                        "Subject",
                        "template",
                        from_email="custom@example.com",
                    )

                    assert mock_email_class.called
                    kwargs = mock_email_class.call_args.kwargs
                    assert kwargs["from_email"] == "custom@example.com"


def test_send_email_helper_no_config(app):
    app.config["MAIL_USERNAME"] = None
    msg = MagicMock()
    with app.app_context():
        _send_email_helper(app, msg)
        assert not msg.send.called


def test_send_async_email_no_default_sender(app):
    del app.config["MAIL_DEFAULT_SENDER"]
    with app.test_request_context():
        with patch("shopyo.api.email.render_template", return_value="content"):
            with patch("shopyo.api.email.print") as mock_print:
                send_async_email("to@example.com", "Subject", "template")
                mock_print.assert_called()


def test_send_email_helper_missing_username(app):
    del app.config["MAIL_USERNAME"]
    msg = MagicMock()
    with app.app_context():
        _send_email_helper(app, msg)
        assert not msg.send.called


def test_send_email_helper_missing_password(app):
    del app.config["MAIL_PASSWORD"]
    msg = MagicMock()
    with app.app_context():
        _send_email_helper(app, msg)
        assert not msg.send.called


def test_send_email_helper_success(app):
    msg = MagicMock()
    msg.send = MagicMock()
    with app.app_context():
        _send_email_helper(app, msg)
        msg.send.assert_called_once()
