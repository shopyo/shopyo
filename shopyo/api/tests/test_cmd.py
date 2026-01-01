import os
import pytest
import sys
from unittest.mock import patch, MagicMock
from shopyo.api.cmd import (
    clean,
    create_module,
    create_box,
    createmodulebox,
    initialise,
    collect_static,
    create_module_in_box,
)


@pytest.fixture
def mock_app():
    app = MagicMock()
    return app


def test_clean_cmd(mock_app):
    # Mocking 'from init import db'
    mock_db = MagicMock()
    with patch("shopyo.api.cmd.db", mock_db), patch(
        "shopyo.api.cmd.tryrmcache"
    ) as mock_rmcache, patch("shopyo.api.cmd.tryrmfile") as mock_rmfile, patch(
        "shopyo.api.cmd.tryrmtree"
    ) as mock_rmtree:

        # We also need to mock the context manager
        mock_app.test_request_context.return_value.__enter__.return_value = MagicMock()

        clean(mock_app)
        mock_db.drop_all.assert_called_once()
        mock_rmcache.assert_called_once()
        mock_rmfile.assert_called_once()
        mock_rmtree.assert_called_once()


@patch("shopyo.api.cmd.trymkdir")
@patch("shopyo.api.cmd.trymkfile")
def test_create_module_cmd(mock_mkfile, mock_mkdir):
    create_module("testmod")
    mock_mkdir.assert_called()
    mock_mkfile.assert_called()


@patch("shopyo.api.cmd.trymkdir")
@patch("shopyo.api.cmd.trymkfile")
def test_create_box_cmd(mock_mkfile, mock_mkdir):
    with patch("shopyo.api.cmd.os.path.exists", return_value=False):
        create_box("testbox")
        mock_mkdir.assert_called_once()
        mock_mkfile.assert_called_once()


@patch("shopyo.api.cmd.create_module")
@patch("shopyo.api.cmd.create_box")
def test_createmodulebox(mock_create_box, mock_create_module):
    # Test module
    res = createmodulebox("testmod")
    assert res[0] is True
    mock_create_module.assert_called_with("testmod")

    # Test box
    res = createmodulebox("box__test")
    assert res[0] is True
    mock_create_box.assert_called_with("box__test")

    # Test module in box
    with patch("shopyo.api.cmd.create_module_in_box") as mock_mod_in_box:
        res = createmodulebox("box__test/mod")
        assert res[0] is True
        mock_mod_in_box.assert_called_with("mod", "box__test")


@patch("shopyo.api.cmd.os.path.exists", return_value=True)
@patch("shopyo.api.cmd.tryrmtree")
@patch("shopyo.api.cmd.get_folders", return_value=[])
def test_collect_static(mock_get_folders, mock_rmtree, mock_exists):
    collect_static()
    mock_rmtree.assert_called()


@patch("shopyo.api.cmd.os.path.exists")
@patch("shopyo.api.cmd.create_module")
def test_create_module_in_box(mock_create_module, mock_exists):
    # Success case
    mock_exists.side_effect = [True, False]  # box exists, module doesn't
    create_module_in_box("mod", "box__test")
    mock_create_module.assert_called_once()

    # Box doesn't exist
    mock_exists.side_effect = [False]
    with patch("shopyo.api.cmd.os.listdir", return_value=[]):
        create_module_in_box("mod", "box__test")
        # Should print and not call create_module
        assert mock_create_module.call_count == 1
