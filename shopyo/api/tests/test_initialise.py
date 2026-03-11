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
        # Create a dummy app.py so with_appcontext doesn't fail immediately
        with open("app.py", "w") as f:
            f.write(
                "from flask import Flask\ndef create_app(config_name='development'): return Flask(__name__)\n"
            )

        # We also need to add current dir to sys.path so 'import app' works
        import sys

        original_path = sys.path[:]
        sys.path.insert(0, os.getcwd())
        try:
            result = runner.invoke(cli, ["initialise"])
        finally:
            sys.path = original_path

        assert result.exit_code != 0
        assert "modules' folder not found" in result.output
        # assert "Modules folder not found" in result.output or "Error" in result.output
