from shopyo.api import html
from markupsafe import escape


def test_notify_xss_protection():
    dangerous_msg = "<script>alert(1)</script>"
    escaped_msg = str(escape(dangerous_msg))
    result = html.notify(dangerous_msg)
    assert dangerous_msg not in result
    assert escaped_msg in result
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in result


def test_notify_success_icon():
    result = html.notify_success("OK")
    assert "fa-check-circle" in result


def test_notify_danger_icon():
    result = html.notify_danger("Error")
    assert "fa-exclamation-circle" in result


def test_notify_warning_icon():
    result = html.notify_warning("Caution")
    assert "fa-exclamation-triangle" in result


def test_notify_info_icon():
    result = html.notify_info("Info")
    assert "fa-info-circle" in result


def test_notify_unknown_type():
    result = html.notify("test", "unknown")
    assert "fa-info-circle" in result
