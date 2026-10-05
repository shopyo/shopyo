import sys

import click


def cli_error(message, hint=None):
    click.secho(f" ❌ Error: {message}", fg="red", bold=True, err=True)
    if hint:
        click.echo(f"    💡 {hint}", err=True)
    sys.exit(1)


def cli_warning(message):
    click.secho(f" ⚠️  {message}", fg="yellow", err=True)


def cli_success(message):
    click.secho(f" ✅ {message}", fg="green", bold=True)


def cli_info(message):
    click.secho(f" ℹ️  {message}", fg="bright_black")


def cli_step(message):
    click.secho(f" ➜ {message}", fg="cyan")


def cli_progress(message, done=False):
    if done:
        click.echo(f"\r ✅ {message}")
    else:
        click.echo(f"\r ⏳ {message}", nl=False)
        sys.stdout.flush()
