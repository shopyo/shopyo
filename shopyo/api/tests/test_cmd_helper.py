import os
import json
import pytest
import sys
from unittest.mock import patch, MagicMock
from shopyo.api.cmd_helper import (
    _clean,
    _collectstatic,
    _upload_data,
    _create_box,
    _create_module,
    _verify_app,
    _verify_box,
    _audit,
    _rename_app,
    _run_app,
)


@pytest.fixture
def mock_app():
    app = MagicMock()
    app.extensions = {"sqlalchemy": MagicMock()}
    return app


def test_clean(mock_app):
    with patch("shopyo.api.cmd_helper.current_app", mock_app), patch(
        "shopyo.api.cmd_helper.tryrmfile"
    ) as mock_rmfile, patch("shopyo.api.cmd_helper.tryrmcache") as mock_rmcache, patch(
        "shopyo.api.cmd_helper.tryrmtree"
    ) as mock_rmtree:

        _clean(verbose=True)

        mock_app.extensions["sqlalchemy"].db.drop_all.assert_called_once()
        mock_rmfile.assert_called_once()
        mock_rmcache.assert_called_once()
        mock_rmtree.assert_called_once()


@patch("shopyo.api.cmd_helper.os.path.exists")
@patch("shopyo.api.cmd_helper.tryrmtree")
@patch("shopyo.api.cmd_helper.get_folders")
def test_collectstatic(mock_get_folders, mock_rmtree, mock_exists):
    mock_exists.return_value = True
    mock_get_folders.return_value = ["app1", "box__test"]

    with patch("shopyo.api.cmd_helper.importlib.import_module"), patch(
        "shopyo.api.cmd_helper.sys.exit"
    ) as mock_exit:

        with patch.dict("sys.modules", {"init": MagicMock(installed_packages=[])}):
            _collectstatic()
            mock_rmtree.assert_called()


@patch("shopyo.api.cmd_helper.trymkdir")
def test_create_box(mock_mkdir):
    with patch("builtins.open", create=True) as mock_open:
        _create_box("testbox")
        mock_mkdir.assert_called_once_with(
            os.path.join("modules", "testbox"), verbose=False
        )
        mock_open.assert_called()


@patch("shopyo.api.cmd_helper.trymkdir")
@patch("shopyo.api.cmd_helper.trymkfile")
def test_create_module(mock_mkfile, mock_mkdir):
    with patch("builtins.open", create=True) as mock_open:
        _create_module("testmod")
        mock_mkdir.assert_called()
        mock_mkfile.assert_called()
        mock_open.assert_called()


@patch("shopyo.api.cmd_helper.path_exists")
def test_verify_app(mock_path_exists):
    mock_path_exists.return_value = True
    info_json = {"module_name": "testapp", "url_prefix": "/testapp"}
    with patch("builtins.open", create=True), patch(
        "json.load", return_value=info_json
    ):
        res = _verify_app("modules/testapp", [])
        assert res["path"] == "modules/testapp"
        assert res["issues"] == []


def test_rename_app():
    with patch("shopyo.api.cmd_helper.os.rename") as mock_rename, patch(
        "shopyo.api.cmd_helper.path_exists", return_value=True
    ), patch("builtins.open", create=True), patch(
        "json.load", return_value={"module_name": "old"}
    ), patch(
        "json.dump"
    ):

        _rename_app("old", "new")
        mock_rename.assert_called_once()


@patch("shopyo.api.cmd_helper.get_folders")
@patch("shopyo.api.cmd_helper.path_exists", return_value=True)
@patch("shopyo.api.cmd_helper.click.echo")
def test_audit(mock_echo, mock_exists, mock_get_folders):
    mock_get_folders.side_effect = [["app1"], ["box__test"], ["subapp1"]]

    info_json = {"module_name": "app1", "url_prefix": "/app1"}
    box_info = {"box_name": "testbox"}

    def mock_open(path, *args, **kwargs):
        m = MagicMock()
        if "info.json" in path:
            m.__enter__.return_value = MagicMock()
            return m
        elif "box_info.json" in path:
            m.__enter__.return_value = MagicMock()
            return m
        return MagicMock()

    with patch("builtins.open", side_effect=mock_open), patch(
        "json.load"
    ) as mock_json_load:

        mock_json_load.side_effect = [info_json, box_info, info_json]
        _audit(True, True, True)
        mock_echo.assert_called()


@patch("shopyo.api.cmd_helper.run")
@patch("shopyo.api.cmd_helper.os.path.exists", return_value=True)
def test_run_app(mock_exists, mock_run):
    _run_app("development")
    mock_run.assert_called_once()
    assert os.environ["FLASK_ENV"] == "development"
