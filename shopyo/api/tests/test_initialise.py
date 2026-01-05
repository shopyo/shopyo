import os
import pytest
from click.testing import CliRunner
from shopyo.api.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_initialise_no_modules_folder(runner, tmp_path):
    """
    Test that shopyo initialise fails gracefully when run in a directory
    without a 'modules' folder.
    """
    # Create a temp directory without 'modules'
    d = tmp_path / "not_a_project"
    d.mkdir()

    with runner.isolated_filesystem(temp_dir=d):
        # We need to mock with_appcontext or ensure it doesn't crash before our check
        # Since initialise has @with_appcontext, it might fail even earlier if no app.py

        result = runner.invoke(cli, ["initialise"])

        assert result.exit_code != 0
        assert "modules' folder not found" in result.output
        # assert "Modules folder not found" in result.output or "Error" in result.output
