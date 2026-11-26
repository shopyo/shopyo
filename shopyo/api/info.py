import datetime
import os
import sys
from pathlib import Path

import click

from shopyo import __version__

logo = r"""
  ____  _
 / ___|| |__   ___  _ __  _   _  ___
 \___ \| '_ \ / _ \| '_ \| | | |/ _ \
  ___) | | | | (_) | |_) | |_| | (_) |
 |____/|_| |_|\___/| .__/ \__, |\___/
                    |_|    |___/
"""

STAR_URL = "https://github.com/shopyo/shopyo"


def _is_quiet():
    return os.environ.get("SHOPYO_QUIET") == "True"


def printinfo():
    """Print the Shopyo banner (logo and version).

    Kept short on purpose: Click already prints the command list in
    ``--help``, so repeating it here was just noise.
    """
    if _is_quiet():
        return

    click.secho(logo, fg="cyan", bold=True)
    click.secho(
        f" Shopyo v{__version__}  ·  © {datetime.datetime.now().year}",
        fg="bright_black",
    )
    click.echo("")


def _star_marker_path():
    base = os.environ.get("SHOPYO_STATE_DIR")
    if not base:
        if os.name == "nt":
            base = os.environ.get("APPDATA") or os.path.expanduser("~")
        else:
            base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
                os.path.expanduser("~"), ".config"
            )
    if not base:
        return None
    return Path(base) / "shopyo" / "star_prompt_shown"


def print_star_message(force=False):
    """Ask once per install for a GitHub star.

    The message is skipped for non-interactive output (pipes, CI, test
    runners) and can be disabled with ``SHOPYO_QUIET=True`` or
    ``SHOPYO_NO_STAR=1``. ``SHOPYO_STATE_DIR`` overrides where the
    "already shown" marker is stored.
    """
    if _is_quiet() or os.environ.get("SHOPYO_NO_STAR"):
        return

    if not force and not sys.stderr.isatty():
        return

    marker = _star_marker_path()
    if marker is None:
        return

    try:
        if marker.exists():
            return
    except OSError:
        return

    click.secho(
        "\n ⭐ Enjoying Shopyo? Support the project with a star:",
        fg="yellow",
        err=True,
    )
    click.secho(f"    {STAR_URL}", fg="cyan", err=True)
    click.echo("", err=True)

    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch()
    except OSError:
        # Read-only home/config dir: show the message again next time.
        pass
