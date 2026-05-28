from unittest.mock import patch, MagicMock
import importlib as real_importlib
import os
import sys
import pytest
from shopyo.api.database import autoload_models


def test_autoload_models(tmp_path):
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    (modules_dir / "box__default" / "auth").mkdir(parents=True)
    (modules_dir / "test_module").mkdir(parents=True)

    class ModelBase:
        pass

    class MyModel(ModelBase):
        __name__ = "MyModel"

    mock_init = MagicMock()
    mock_init.installed_packages = ["plugin1"]
    mock_init.db.Model = ModelBase

    mod_with_models = MagicMock()
    mod_with_models.__dir__ = MagicMock(return_value=["MyModel"])
    mod_with_models.MyModel = MyModel

    with patch.dict("sys.modules", {"init": mock_init}):
        with patch("shopyo.api.database.importlib") as mock_importlib:
            with patch("shopyo.api.database.click"):
                mock_importlib.import_module.return_value = mod_with_models
                cwd = os.getcwd()
                try:
                    os.chdir(tmp_path)
                    autoload_models(verbose=True)
                finally:
                    os.chdir(cwd)

                mock_importlib.import_module.assert_any_call(
                    "modules.box__default.auth.models"
                )
                mock_importlib.import_module.assert_any_call(
                    "modules.test_module.models"
                )
                mock_importlib.import_module.assert_any_call("plugin1.models")


def test_autoload_models_no_installed_packages(tmp_path):
    (tmp_path / "modules").mkdir()

    mock_init = MagicMock(spec=[])

    with patch.dict("sys.modules", {"init": mock_init}):
        with patch("shopyo.api.database.importlib"):
            with patch("shopyo.api.database.click"):
                cwd = os.getcwd()
                try:
                    os.chdir(tmp_path)
                    autoload_models(verbose=False)
                finally:
                    os.chdir(cwd)


def test_autoload_models_init_import_error(tmp_path):
    (tmp_path / "modules").mkdir()

    with patch.dict("sys.modules", {"init": MagicMock(side_effect=ImportError)}):
        with patch("shopyo.api.database.importlib"):
            with patch("shopyo.api.database.click"):
                cwd = os.getcwd()
                try:
                    os.chdir(tmp_path)
                    autoload_models(verbose=False)
                finally:
                    os.chdir(cwd)


def test_autoload_models_module_import_error(tmp_path):
    (tmp_path / "modules" / "broken_mod").mkdir(parents=True)

    with patch("shopyo.api.database.importlib") as mock_importlib:
        with patch("shopyo.api.database.click") as mock_click:
            mock_click.echo = MagicMock()

            def import_side(name):
                if "broken_mod" in name:
                    raise ImportError("no module")
                return MagicMock()

            mock_importlib.import_module.side_effect = import_side

            cwd = os.getcwd()
            try:
                os.chdir(tmp_path)
                autoload_models(verbose=True)
            finally:
                os.chdir(cwd)

            error_calls = [c for c in mock_click.echo.call_args_list if "[ ]" in str(c)]
            assert len(error_calls) >= 1


def test_autoload_models_box_import_error(tmp_path):
    (tmp_path / "modules" / "box__shop" / "checkout").mkdir(parents=True)

    with patch("shopyo.api.database.importlib") as mock_importlib:
        with patch("shopyo.api.database.click") as mock_click:
            mock_click.echo = MagicMock()

            def import_side(name):
                if "checkout" in name:
                    raise ImportError("box error")
                return MagicMock()

            mock_importlib.import_module.side_effect = import_side

            cwd = os.getcwd()
            try:
                os.chdir(tmp_path)
                autoload_models(verbose=True)
            finally:
                os.chdir(cwd)

            error_calls = [c for c in mock_click.echo.call_args_list if "[ ]" in str(c)]
            assert len(error_calls) >= 1


def test_autoload_models_installed_packages_error(tmp_path):
    (tmp_path / "modules" / "mymod").mkdir(parents=True)

    mock_init = MagicMock()
    mock_init.installed_packages = ["broken_plugin"]

    with patch.dict("sys.modules", {"init": mock_init}):
        with patch("shopyo.api.database.importlib") as mock_importlib:
            with patch("shopyo.api.database.click") as mock_click:
                mock_click.echo = MagicMock()

                call_count = 0

                def import_side(name):
                    nonlocal call_count
                    call_count += 1
                    if "broken_plugin" in name:
                        raise Exception("plugin failed")
                    return MagicMock()

                mock_importlib.import_module.side_effect = import_side

                cwd = os.getcwd()
                try:
                    os.chdir(tmp_path)
                    autoload_models(verbose=True)
                finally:
                    os.chdir(cwd)

                error_calls = [
                    c for c in mock_click.echo.call_args_list if "[ ]" in str(c)
                ]
                assert len(error_calls) >= 1


def test_autoload_models_skip_pycache_json(tmp_path):
    (tmp_path / "modules" / "box__test" / "real_mod").mkdir(parents=True)
    (tmp_path / "modules" / "__pycache__").mkdir(exist_ok=True)
    (tmp_path / "modules" / "box__test" / "__pycache__").mkdir(exist_ok=True)
    (tmp_path / "modules" / "box__test" / "box_info.json").write_text("{}")

    mock_init = MagicMock()
    mock_init.installed_packages = []

    with patch.dict("sys.modules", {"init": mock_init}):
        with patch("shopyo.api.database.importlib") as mock_importlib:
            with patch("shopyo.api.database.click"):
                mock_importlib.import_module.return_value = MagicMock()

                cwd = os.getcwd()
                try:
                    os.chdir(tmp_path)
                    autoload_models(verbose=False)
                finally:
                    os.chdir(cwd)

                mock_importlib.import_module.assert_called_once_with(
                    "modules.box__test.real_mod.models"
                )


def test_autoload_models_extensions(tmp_path):
    (tmp_path / "modules").mkdir()

    mock_init = MagicMock()
    mock_init.installed_packages = []

    mock_app = MagicMock()
    mock_app.extensions = {"shopyo_mypkg": MagicMock(), "not_shopyo": MagicMock()}

    with patch.dict("sys.modules", {"init": mock_init}):
        with patch("shopyo.api.database.importlib") as mock_importlib:
            with patch("shopyo.api.database.click"):
                with patch("flask.current_app", mock_app):
                    call_count = 0

                    def import_side(name):
                        nonlocal call_count
                        call_count += 1
                        if "shopyo_mypkg" in name and call_count == 1:
                            raise ImportError("no models")
                        return MagicMock()

                    mock_importlib.import_module.side_effect = import_side

                    cwd = os.getcwd()
                    try:
                        os.chdir(tmp_path)
                        autoload_models(verbose=False)
                    finally:
                        os.chdir(cwd)

                    mock_importlib.import_module.assert_any_call("shopyo_mypkg.models")
                    assert not any(
                        "not_shopyo" in str(c)
                        for c in mock_importlib.import_module.call_args_list
                    )


def test_autoload_models_extensions_verbose_with_models(tmp_path):
    (tmp_path / "modules").mkdir()

    class ModelBase:
        pass

    class MyModel(ModelBase):
        __name__ = "MyModel"

    mock_init = MagicMock()
    mock_init.installed_packages = []
    mock_init.db.Model = ModelBase

    mod_with_model = MagicMock()
    mod_with_model.__dir__ = MagicMock(return_value=["MyModel"])
    mod_with_model.MyModel = MyModel

    mock_app = MagicMock()
    mock_app.extensions = {"shopyo_blog": MagicMock()}

    with patch.dict("sys.modules", {"init": mock_init}):
        with patch("shopyo.api.database.importlib") as mock_importlib:
            with patch("shopyo.api.database.click") as mock_click:
                mock_click.echo = MagicMock()
                with patch("flask.current_app", mock_app):
                    mock_importlib.import_module.return_value = mod_with_model

                    cwd = os.getcwd()
                    try:
                        os.chdir(tmp_path)
                        autoload_models(verbose=True)
                    finally:
                        os.chdir(cwd)

                    mock_importlib.import_module.assert_any_call("shopyo_blog.models")


def test_autoload_models_extensions_exception(tmp_path):
    (tmp_path / "modules").mkdir()

    mock_init = MagicMock()
    mock_init.installed_packages = []

    mock_app = MagicMock()
    mock_app.extensions = {"shopyo_plugin": MagicMock()}

    with patch.dict("sys.modules", {"init": mock_init}):
        with patch("shopyo.api.database.importlib") as mock_importlib:
            with patch("shopyo.api.database.click") as mock_click:
                mock_click.echo = MagicMock()
                with patch("flask.current_app", mock_app):

                    def import_side(name):
                        if "shopyo_plugin" in name:
                            raise Exception("generic error")
                        return MagicMock()

                    mock_importlib.import_module.side_effect = import_side

                    cwd = os.getcwd()
                    try:
                        os.chdir(tmp_path)
                        autoload_models(verbose=True)
                    finally:
                        os.chdir(cwd)

                    error_calls = [
                        c
                        for c in mock_click.echo.call_args_list
                        if "Error loading" in str(c)
                    ]
                    assert len(error_calls) >= 1


def test_autoload_models_no_app_context(tmp_path):
    (tmp_path / "modules").mkdir()

    with patch("shopyo.api.database.importlib"):
        with patch("shopyo.api.database.click"):
            cwd = os.getcwd()
            try:
                os.chdir(tmp_path)
                autoload_models(verbose=False)
            finally:
                os.chdir(cwd)
