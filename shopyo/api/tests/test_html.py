from shopyo.api import html
from markupsafe import escape


def test_notify():
    message = "Hello World"
    alert_type = "primary"

    result = html.notify(message, alert_type)

    assert message in result
    assert f"alert-{alert_type}" in result
    assert "shopyo-alert" in result
    assert "setTimeout" in result


def test_notify_xss_protection():
    # Test that dangerous characters are escaped
    dangerous_msg = "<script>alert(1)</script>"
    escaped_msg = str(escape(dangerous_msg))

    result = html.notify(dangerous_msg)

    assert dangerous_msg not in result
    assert escaped_msg in result
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in result


def test_notify_helpers():
    msg = "test message"

    # Success
    res = html.notify_success(msg)
    assert "alert-success" in res
    assert msg in res

    # Danger
    res = html.notify_danger(msg)
    assert "alert-danger" in res
    assert msg in res

    # Warning
    res = html.notify_warning(msg)
    assert "alert-warning" in res
    assert msg in res

    # Info
    res = html.notify_info(msg)
    assert "alert-info" in res
    assert msg in res
