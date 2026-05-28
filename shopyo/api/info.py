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
    import os

    if os.environ.get("SHOPYO_QUIET") == "True":
        return
    """
    prints Shopyo copyright in ASCII art font
    """
    click.secho(logo, fg="cyan", bold=True)
    click.secho(
        f" Shopyo Framework © {datetime.datetime.now().year}", fg="bright_black"
    )
    click.echo(" " + "─" * 32 + "\n")
    click.secho(" 📖 Available commands:", fg="cyan")
    click.echo("    new          Scaffold a new Flask project")
    click.echo("    startapp     Create a new module inside your project")
    click.echo("    startbox     Create a new box (group of modules)")
    click.echo("    initialise   Initialize the database and migrations")
    click.echo("    run          Run the development server")
    click.echo("    collectstatic Collect static files for production")
    click.echo("    audit        Audit modules for issues")
    click.echo("    env          Generate .env file")
    click.echo("    clean        Clean workspace")
    click.echo(
        "\n 💡 Quick start: shopyo new myproject && cd myproject && shopyo initialise && flask run --debug"
    )
    click.echo("")
