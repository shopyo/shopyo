from shopyo.api import html
from markupsafe import escape


def test_notify_xss_protection():
    # Test that dangerous characters are escaped
    dangerous_msg = "<script>alert(1)</script>"
    escaped_msg = str(escape(dangerous_msg))

    result = html.notify(dangerous_msg)

    assert dangerous_msg not in result
    assert escaped_msg in result
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in result
