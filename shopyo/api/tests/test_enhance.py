from shopyo.api.enhance import base_context


def test_base_context():
    assert isinstance(base_context(), dict)
