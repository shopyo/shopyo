import os
from unittest.mock import patch, MagicMock
from shopyo.api import info


def test_printinfo_quiet(monkeypatch):
    monkeypatch.setenv("SHOPYO_QUIET", "True")
    with patch("shopyo.api.info.click.secho") as mock_secho:
        info.printinfo()
        mock_secho.assert_not_called()


def test_printinfo_displays(monkeypatch):
    monkeypatch.delenv("SHOPYO_QUIET", raising=False)
    with patch("shopyo.api.info.click.secho") as mock_secho:
        with patch("shopyo.api.info.click.echo") as mock_echo:
            info.printinfo()
            assert mock_secho.called
            assert mock_echo.called
