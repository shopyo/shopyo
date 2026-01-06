from shopyo.api import enhance


def test_base_context():
    context = enhance.base_context()
    assert isinstance(context, dict)
    assert context == {}

    # Ensure it returns a copy
    context["test"] = "value"
    context2 = enhance.base_context()
    assert context2 == {}
