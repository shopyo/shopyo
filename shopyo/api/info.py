import datetime
import click

logo = r"""
  ____  _
 / ___|| |__   ___  _ __  _   _  ___
 \___ \| '_ \ / _ \| '_ \| | | |/ _ \
  ___) | | | | (_) | |_) | |_| | (_) |
 |____/|_| |_|\___/| .__/ \__, |\___/
                   |_|    |___/
"""


def printinfo():
    """
    prints Shopyo copyright in ASCII art font
    """
    click.secho(logo, fg="cyan", bold=True)
    click.secho(
        f" Shopyo Framework © {datetime.datetime.now().year}", fg="bright_black"
    )
    click.echo(" " + "─" * 32 + "\n")
