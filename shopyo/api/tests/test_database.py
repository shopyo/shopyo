from unittest.mock import patch, MagicMock
import os
import sys
from shopyo.api.database import autoload_models


def test_autoload_models():
    # Mock os.listdir to simulate a modules directory
    def listdir_side_effect(path):
        if path == "modules":
            return ["box__default", "test_module"]
        if path == os.path.join("modules", "box__default"):
            return ["auth"]
        return []

    # Mock init module
    mock_init = MagicMock()
    mock_init.installed_packages = ["plugin1"]

    with patch.dict("sys.modules", {"init": mock_init}):
        with patch("shopyo.api.database.os.listdir", side_effect=listdir_side_effect):
            # Patch import_module in the database module's namespace
            with patch("shopyo.api.database.importlib.import_module") as mock_import:
                with patch("shopyo.api.database.click.echo"):
                    autoload_models(verbose=True)

                    # Check some expected imports
                    mock_import.assert_any_call("modules.box__default.auth.models")
                    mock_import.assert_any_call("modules.test_module.models")
                    mock_import.assert_any_call("plugin1.models")
