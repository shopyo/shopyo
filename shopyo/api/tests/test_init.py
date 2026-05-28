from unittest.mock import patch, MagicMock
import pytest
from flask import Flask
from shopyo.init import load_extensions, load_user, db as real_db


def test_load_user():
    assert load_user("any_id") is None


def test_load_extensions_basic():
    app = Flask(__name__)
    app.extensions = {}

    with patch("shopyo.init.migrate.init_app") as mock_migrate:
        with patch("shopyo.init.db.init_app"):
            with patch("shopyo.init.mail.init_app") as mock_mail:
                with patch("shopyo.init.login_manager.init_app") as mock_login:
                    with patch("shopyo.init.csrf.init_app") as mock_csrf:
                        load_extensions(app)
                        mock_migrate.assert_called_once_with(app, real_db)
                        mock_mail.assert_called_once_with(app)
                        mock_login.assert_called_once_with(app)
                        mock_csrf.assert_called_once_with(app)


def test_load_extensions_with_plugins():
    app = Flask(__name__)
    mock_ext = MagicMock()
    app.extensions = {"shopyo_mypkg": mock_ext}

    with patch("shopyo.init.importlib") as mock_importlib:
        with patch("shopyo.init.migrate.init_app"):
            with patch("shopyo.init.db.init_app"):
                with patch("shopyo.init.mail.init_app"):
                    with patch("shopyo.init.login_manager.init_app"):
                        with patch("shopyo.init.csrf.init_app"):
                            mock_module = MagicMock()
                            mock_importlib.import_module.return_value = mock_module
                            load_extensions(app)
                            mock_importlib.import_module.assert_called_once_with(
                                "shopyo_mypkg.models"
                            )


def test_load_extensions_plugin_import_error():
    app = Flask(__name__)
    mock_ext = MagicMock()
    app.extensions = {"shopyo_broken": mock_ext}

    with patch("shopyo.init.importlib") as mock_importlib:
        mock_importlib.import_module.side_effect = ImportError("no module")
        with patch("shopyo.init.migrate.init_app"):
            with patch("shopyo.init.db.init_app"):
                with patch("shopyo.init.mail.init_app"):
                    with patch("shopyo.init.login_manager.init_app"):
                        with patch("shopyo.init.csrf.init_app"):
                            with patch("shopyo.init.print") as mock_print:
                                load_extensions(app)
                                mock_print.assert_called_once()


def test_load_extensions_non_shopyo_extension():
    app = Flask(__name__)
    app.extensions = {"some_other_pkg": MagicMock()}

    with patch("shopyo.init.importlib") as mock_importlib:
        with patch("shopyo.init.migrate.init_app"):
            with patch("shopyo.init.db.init_app"):
                with patch("shopyo.init.mail.init_app"):
                    with patch("shopyo.init.login_manager.init_app"):
                        with patch("shopyo.init.csrf.init_app"):
                            load_extensions(app)
                            mock_importlib.import_module.assert_not_called()


def test_load_extensions_plugin_generic_exception():
    app = Flask(__name__)
    mock_ext = MagicMock()
    app.extensions = {"shopyo_crash": mock_ext}

    with patch("shopyo.init.importlib") as mock_importlib:
        mock_importlib.import_module.side_effect = Exception("crash")
        with patch("shopyo.init.migrate.init_app"):
            with patch("shopyo.init.db.init_app"):
                with patch("shopyo.init.mail.init_app"):
                    with patch("shopyo.init.login_manager.init_app"):
                        with patch("shopyo.init.csrf.init_app"):
                            with patch("shopyo.init.print") as mock_print:
                                load_extensions(app)
                                mock_print.assert_called_once()
