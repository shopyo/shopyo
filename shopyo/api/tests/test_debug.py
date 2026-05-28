import os
import pytest
from shopyo.api.debug import is_yo_debug


@pytest.mark.parametrize(
    "value,expected",
    [
        ("1", True),
        ("true", True),
        ("True", True),
        ("yes", True),
        ("YeS", True),
        ("0", False),
        ("false", False),
        ("no", False),
        ("", False),
        ("anything", False),
    ],
)
def test_is_yo_debug(monkeypatch, value, expected):
    monkeypatch.setenv("SHOPYO_DEBUG", value)
    assert is_yo_debug() is expected
