from shopyo.api import enhance


def test_base_context():
    context = enhance.base_context()
    assert isinstance(context, dict)
    assert len(context) == 0

    # Verify it returns a copy
    context["key"] = "value"
    context2 = enhance.base_context()
    assert "key" not in context2
