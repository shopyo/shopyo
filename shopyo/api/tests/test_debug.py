import os
import pytest
from shopyo.api.debug import is_yo_debug


def test_is_yo_debug_false():
    if "SHOPYO_DEBUG" in os.environ:
        old_val = os.environ["SHOPYO_DEBUG"]
        del os.environ["SHOPYO_DEBUG"]
    else:
        old_val = None

    try:
        assert is_yo_debug() is False
    finally:
        if old_val is not None:
            os.environ["SHOPYO_DEBUG"] = old_val


def test_is_yo_debug_true():
    if "SHOPYO_DEBUG" in os.environ:
        old_val = os.environ["SHOPYO_DEBUG"]
    else:
        old_val = None

    try:
        os.environ["SHOPYO_DEBUG"] = "1"
        assert is_yo_debug() is True
        os.environ["SHOPYO_DEBUG"] = "true"
        assert is_yo_debug() is True
        os.environ["SHOPYO_DEBUG"] = "yes"
        assert is_yo_debug() is True
    finally:
        if old_val is not None:
            os.environ["SHOPYO_DEBUG"] = old_val
        else:
            if "SHOPYO_DEBUG" in os.environ:
                del os.environ["SHOPYO_DEBUG"]
