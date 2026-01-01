import os
import pytest
from unittest.mock import patch
from wtforms.validators import ValidationError
from shopyo.api import validators


def test_is_alpha_num_underscore():
    assert validators.is_alpha_num_underscore("valid_name_123") is True
    assert validators.is_alpha_num_underscore("invalid-name") is False
    assert validators.is_alpha_num_underscore("name with space") is False
    assert validators.is_alpha_num_underscore("") is False


def test_is_empty_str():
    assert validators.is_empty_str("") is True
    assert validators.is_empty_str("   ") is True
    assert validators.is_empty_str("not empty") is False


def test_is_valid_slug():
    assert validators.is_valid_slug("valid-slug-123")
    assert validators.is_valid_slug("valid_slug")
    assert not validators.is_valid_slug("invalid slug")
    assert not validators.is_valid_slug("invalid!")


def test_is_valid_url():
    assert validators.is_valid_url("http://google.com")
    assert validators.is_valid_url("https://localhost:8000")
    assert validators.is_valid_url("ftp://fileserver.local/path")
    assert not validators.is_valid_url("not-a-url")


def test_verify_slug():
    class Field:
        def __init__(self, data):
            self.data = data

    validators.verify_slug(None, Field("valid-slug"))

    with pytest.raises(ValidationError):
        validators.verify_slug(None, Field("invalid slug!"))


def test_get_module_path_if_exists(tmp_path):
    # Setup fake modules structure
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()

    box_dir = modules_dir / "box__test"
    box_dir.mkdir()

    mod_in_box = box_dir / "mod1"
    mod_in_box.mkdir()

    standalone_mod = modules_dir / "mod2"
    standalone_mod.mkdir()

    with patch("os.getcwd", return_value=str(tmp_path)):
        # Test standalone module
        assert validators.get_module_path_if_exists("mod2") == str(standalone_mod)

        # Test module in box
        assert validators.get_module_path_if_exists("mod1") == str(mod_in_box)

        # Test box itself
        assert validators.get_module_path_if_exists("box__test") == str(box_dir)

        # Test non-existent
        assert validators.get_module_path_if_exists("nonexistent") is None
