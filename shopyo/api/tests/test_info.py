import os
from unittest.mock import patch, MagicMock
from shopyo.api import info
from shopyo.api.info import print_star_message


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


def test_star_message_shown_only_once(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("SHOPYO_STATE_DIR", str(tmp_path))
    monkeypatch.delenv("SHOPYO_QUIET", raising=False)
    monkeypatch.delenv("SHOPYO_NO_STAR", raising=False)

    print_star_message(force=True)
    err = capsys.readouterr().err
    assert "github.com/shopyo/shopyo" in err
    assert "star" in err.lower()

    print_star_message(force=True)
    assert capsys.readouterr().err == ""


def test_star_message_can_be_disabled(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("SHOPYO_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("SHOPYO_NO_STAR", "1")

    print_star_message(force=True)
    assert capsys.readouterr().err == ""
