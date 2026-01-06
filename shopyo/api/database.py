import importlib
import os
import sys

import click

from shopyo.api.constants import SEP_CHAR
from shopyo.api.constants import SEP_NUM


def autoload_models(verbose=False):
    """
    Auto imports models from modules/ in desired file. Used so that
    flask_migrate does not miss models when migrating

    Returns
    -------
    None
    """
    click.echo("Auto importing models...")
    click.echo(SEP_CHAR * SEP_NUM)

    for folder in os.listdir("modules"):
        if folder.startswith("__"):
            continue
        elif folder.startswith("box__"):
            for sub_folder in os.listdir(os.path.join("modules", folder)):
                if sub_folder.startswith("__"):  # ignore __pycache__
                    continue
                elif sub_folder.endswith(".json"):  # box_info.json
                    continue
                try:
                    to_load_submodel = f"modules.{folder}.{sub_folder}.models"
                    mod = importlib.import_module(to_load_submodel)
                    if verbose:
                        click.echo(f"[x] imported {to_load_submodel}")
                        from init import db

                        for attr_name in dir(mod):
                            attr = getattr(mod, attr_name)
                            if (
                                isinstance(attr, type)
                                and issubclass(attr, db.Model)
                                and attr != db.Model
                            ):
                                click.echo(f"    - Found model: {attr.__name__}")
                except Exception as e:
                    if verbose:
                        click.echo(f"[ ] {e}")
        else:
            try:
                to_load = f"modules.{folder}.models"
                mod = importlib.import_module(to_load)
                if verbose:
                    click.echo(f"[x] imported {to_load}")
                    from init import db

                    for attr_name in dir(mod):
                        attr = getattr(mod, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, db.Model)
                            and attr != db.Model
                        ):
                            click.echo(f"    - Found model: {attr.__name__}")
            except Exception as e:
                if verbose:
                    click.echo(f"[ ] {e}")

    # installed modules
    try:
        from init import installed_packages
    except ImportError:
        installed_packages = []

    for plugin in installed_packages:
        try:
            to_load_models = f"{plugin}.models"
            mod = importlib.import_module(to_load_models)
            if verbose:
                click.echo(f"[x] imported {to_load_models}")
                from init import db

                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, db.Model)
                        and attr != db.Model
                    ):
                        click.echo(f"    - Found model: {attr.__name__}")
        except Exception as e:
            if verbose:
                click.echo(f"[ ] {e}")

    # manually initialized extensions
    try:
        from flask import current_app

        if current_app:
            for ext_name in current_app.extensions:
                if ext_name.startswith("shopyo_"):
                    try:
                        to_load_models = f"{ext_name}.models"
                        mod = importlib.import_module(to_load_models)
                        if verbose:
                            click.echo(f"[x] imported {to_load_models} from extensions")
                            from init import db

                            for attr_name in dir(mod):
                                attr = getattr(mod, attr_name)
                                if (
                                    isinstance(attr, type)
                                    and issubclass(attr, db.Model)
                                    and attr != db.Model
                                ):
                                    click.echo(f"    - Found model: {attr.__name__}")
                    except ImportError:
                        pass
                    except Exception as e:
                        if verbose:
                            click.echo(f"[ ] Error loading models for {ext_name}: {e}")
    except RuntimeError:
        pass  # No application context

    click.echo("")
