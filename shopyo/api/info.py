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
    click.secho(" 📖 Available commands:", fg="cyan")
    click.echo("    startapp     Create a new module")
    click.echo("    startbox     Create a new box")
    click.echo("    initialise   Initialize the database")
    click.echo("    clean        Clean workspace")
    click.echo("    run          Run the development server")
    click.echo("    collectstatic  Collect static files")
    click.echo("    audit        Audit modules for issues")
    click.echo("\n 💡 Tip: Use --help with any command for more info")
    click.echo("        Use -i or --interactive for guided prompts")
    click.echo("")
