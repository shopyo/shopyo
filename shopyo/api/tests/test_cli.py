import os
import sys
import click
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

# Mock app module before importing cli
sys.modules["app"] = MagicMock()
sys.modules["app"].create_app = MagicMock(return_value=MagicMock())
sys.modules["shopyo.app"] = MagicMock()
sys.modules["shopyo.app"].create_app = sys.modules["app"].create_app

from shopyo.api.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_testok(runner):
    result = runner.invoke(cli, ["testok"])
    assert result.exit_code == 0
    assert "test ok!" in result.output


@patch("shopyo.api.cli._create_box")
def test_startbox(mock_create_box, runner):
    original_exists = os.path.exists

    def exists_side_effect(path):
        if "box__test" in path:
            return False
        return original_exists(path)

    with patch("os.path.exists", side_effect=exists_side_effect):
        result = runner.invoke(cli, ["startbox", "box__test"])
        assert result.exit_code == 0
        mock_create_box.assert_called_once_with("box__test", verbose=False)


@patch("shopyo.api.cli._create_box")
def test_startbox_exists(mock_create_box, runner):
    with patch("os.path.exists", return_value=True):
        result = runner.invoke(cli, ["startbox", "box__test"])
        assert result.exit_code == 1
        assert "already exists" in result.output


@patch("shopyo.api.cli._create_module")
@patch("shopyo.api.cli.get_module_path_if_exists")
def test_startapp_simple(mock_get_path, mock_create_module, runner):
    mock_get_path.return_value = None
    result = runner.invoke(cli, ["startapp", "testmod"])
    assert result.exit_code == 0
    mock_create_module.assert_called_once()
    args, kwargs = mock_create_module.call_args
    assert args[0] == "testmod"
    assert kwargs["base_path"] == os.path.join("modules", "", "testmod")


@patch("shopyo.api.cli._create_box")
@patch("shopyo.api.cli._create_module")
@patch("shopyo.api.cli.get_module_path_if_exists")
def test_startapp_in_box(mock_get_path, mock_create_module, mock_create_box, runner):
    mock_get_path.return_value = None
    result = runner.invoke(cli, ["startapp", "testmod", "box__test"])
    assert result.exit_code == 0
    mock_create_module.assert_called_once()
    args, kwargs = mock_create_module.call_args
    assert args[0] == "testmod"
    assert kwargs["base_path"] == os.path.join("modules", "box__test", "testmod")


def test_startapp_invalid_box_name(runner):
    result = runner.invoke(cli, ["startapp", "testmod", "invalidbox"])
    assert result.exit_code == 1
    assert "BOXNAME should start with 'box__'" in result.output


def test_startapp_invalid_mod_name(runner):
    result = runner.invoke(cli, ["startapp", "box_mod"])
    assert result.exit_code == 1
    assert "cannot start with box_" in result.output


@patch("shopyo.api.cli.get_module_path_if_exists")
def test_startapp_already_exists(mock_get_path, runner):
    mock_get_path.return_value = "/some/path"
    result = runner.invoke(cli, ["startapp", "testmod"])
    assert result.exit_code == 1
    assert "already exists" in result.output


@patch("shopyo.api.cli._collectstatic")
def test_collectstatic(mock_collect, runner):
    result = runner.invoke(cli, ["collectstatic"])
    assert result.exit_code == 0
    mock_collect.assert_called_once_with(target_module="modules", verbose=False)

    result = runner.invoke(cli, ["collectstatic", "modules/auth"])
    assert result.exit_code == 0
    mock_collect.assert_called_with(target_module="modules/auth", verbose=False)


@patch("shopyo.api.cli._clean")
def test_clean(mock_clean, runner):
    result = runner.invoke(cli, ["clean"])
    assert result.exit_code == 0
    mock_clean.assert_called_once_with(
        verbose=False, clear_migration=True, clear_db=True
    )


@patch("shopyo.api.cli._clean")
@patch("shopyo.api.cli.autoload_models")
@patch("shopyo.api.cli.run")
@patch("shopyo.api.cli._collectstatic")
@patch("shopyo.api.cli._upload_data")
def test_initialise(
    mock_upload, mock_collect, mock_run, mock_autoload, mock_clean, runner
):
    result = runner.invoke(cli, ["initialise"])
    assert result.exit_code == 0
    mock_clean.assert_called_once()
    assert mock_autoload.call_count == 2
    assert mock_run.call_count == 3  # init, migrate, upgrade
    mock_collect.assert_called_once()
    mock_upload.assert_called_once()


@patch("shopyo.api.cli._run_app")
def test_rundebug(mock_run, runner):
    result = runner.invoke(cli, ["rundebug"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("development")


@patch("shopyo.api.cli._run_app")
def test_runserver(mock_run, runner):
    result = runner.invoke(cli, ["runserver"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("production")


@patch("shopyo.api.cli._audit")
def test_audit(mock_audit, runner):
    result = runner.invoke(cli, ["audit"])
    assert result.exit_code == 0
    mock_audit.assert_called_once_with(True, True, True)

    result = runner.invoke(cli, ["audit", "--show-warning"])
    assert result.exit_code == 0
    mock_audit.assert_called_with(True, False, False)


@patch("shopyo.api.cli._rename_app")
def test_rename(mock_rename, runner):
    result = runner.invoke(cli, ["rename", "old", "new"])
    assert result.exit_code == 0
    mock_rename.assert_called_once_with("old", "new")


@patch("shopyo.api.cli.copytree")
@patch("shopyo.api.file.trymkfile")
@patch("shopyo.api.file.trymkdir")
@patch("shopyo.api.file.tryrmtree")
def test_new(mock_rmtree, mock_mkdir, mock_mkfile, mock_copytree, runner):
    # We need to patch shopyo.__version__ but since we might not invoke the real init,
    # we can try to patch where it is used or mocking the module.
    # The 'new' command imports it inside the function: from shopyo import __version__

    original_exists = os.path.exists

    def exists_side_effect(path):
        if path == "/tmp":
            return True
        if "myproj" in path or path.endswith("tmp/tmp"):
            return False
        return original_exists(path)

    with patch("shopyo.__version__", "1.0.0", create=True), patch(
        "os.getcwd", return_value="/tmp"
    ), patch("os.path.exists", side_effect=exists_side_effect):

        # Test default (current dir)
        result = runner.invoke(cli, ["new"])
        if result.exit_code != 0:
            print(result.output)
            print(result.exception)

        assert result.exit_code == 0
        assert "creating project" in result.output

        # Test with project name
        result = runner.invoke(cli, ["new", "myproj"])
        assert result.exit_code == 0
        assert "creating project myproj" in result.output


@patch("shopyo.api.cli.copytree")
def test_new_exists(mock_copytree, runner):
    with patch("shopyo.__version__", "1.0.0", create=True), patch(
        "os.getcwd", return_value="/tmp"
    ), patch("os.path.exists", return_value=True):

        result = runner.invoke(cli, ["new", "myproj"])
        assert result.exit_code == 1
        assert "Unable to create new project" in result.output
