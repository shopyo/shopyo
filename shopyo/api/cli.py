import os
import sys
from pathlib import Path
from shutil import copytree
from shutil import ignore_patterns
from subprocess import PIPE
from subprocess import run

import click
from flask.cli import FlaskGroup
from flask.cli import pass_script_info
from flask.cli import with_appcontext

from shopyo.api.cmd_helper import _audit
from shopyo.api.cmd_helper import _clean
from shopyo.api.cmd_helper import _collectstatic
from shopyo.api.cmd_helper import _create_box
from shopyo.api.cmd_helper import _create_module
from shopyo.api.cmd_helper import _rename_app
from shopyo.api.cmd_helper import _run_app
from shopyo.api.cmd_helper import _upload_data
from shopyo.api.constants import SEP_CHAR
from shopyo.api.constants import SEP_NUM
from shopyo.api.database import autoload_models
from shopyo.api.file import tryrmtree
from shopyo.api.info import printinfo
from shopyo.api.validators import get_module_path_if_exists
from shopyo.api.validators import is_alpha_num_underscore


def _create_shopyo_app():
    sys.path.append(os.getcwd())
    try:
        import app

        create_app = app.create_app
    except ImportError as e:
        click.secho(
            f" ❌ Error: Could not find 'app' module.",
            fg="red",
            bold=True,
        )
        click.echo(f"    Details: {e}")
        click.echo("\n 💡 Make sure you are in your Shopyo project root directory.")
        click.echo(
            "    Your project should have an 'app.py' file with a 'create_app' function."
        )
        sys.exit(1)
    except AttributeError as e:
        click.secho(
            f" ❌ Error: Could not find 'create_app' in 'app.py'.",
            fg="red",
            bold=True,
        )
        click.echo(f"    Details: {e}")
        click.echo(
            "\n 💡 Your 'app.py' should define a 'create_app(config_name)' function."
        )
        click.echo("    Example:")
        click.echo("        def create_app(config_name='development'):")
        click.echo("            app = Flask(__name__)")
        click.echo("            # ... initialize extensions and modules")
        click.echo("            return app")
        sys.exit(1)

    config_name = os.environ.get("SHOPYO_CONFIG_PROFILE") or "development"
    return create_app(config_name=config_name)


@click.group(cls=FlaskGroup, create_app=_create_shopyo_app)
@click.option("--config", default="development", help="Flask app configuration type")
@pass_script_info
def cli(info, **parmams):
    """CLI for shopyo"""
    printinfo()
    config_name = parmams["config"]
    info.data["config"] = config_name
    os.environ["FLASK_APP"] = f"app:create_app('{config_name}')"
    os.environ["FLASK_ENV"] = config_name
    os.environ["ENV"] = config_name


@cli.command("startbox", with_appcontext=False)
@click.argument("boxname", required=False)
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option("--interactive", "-i", is_flag=True, default=False)
def create_box(boxname, verbose, interactive):
    """creates ``box`` with ``box_info.json``.

    ``BOXNAME`` is the name of the ``box`` which holds modules

    Use --interactive or -i to be prompted for box name.
    """
    if interactive or boxname is None:
        boxname = click.prompt(
            " 📦 Enter box name",
            type=str,
            default="box__mybox",
            show_default=True,
        )
        if not boxname.startswith("box__"):
            click.secho(
                " ⚠️  Box name should start with 'box__' prefix. Adding automatically...",
                fg="yellow",
            )
            boxname = "box__" + boxname

    path = os.path.join("modules", boxname)

    if os.path.exists(os.path.join("modules", boxname)):
        click.secho(
            f" ❌ Error: Box '{path}' already exists!", fg="red", bold=True, err=True
        )
        sys.exit(1)

    _create_box(boxname, verbose=verbose)


@cli.command("startapp", with_appcontext=False)
@click.argument("modulename", required=False)
@click.argument("boxname", required=False, default="")
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option("--interactive", "-i", is_flag=True, default=False)
def create_module(modulename, boxname, verbose, interactive):
    """
    create a module/app ``MODULENAME`` inside ``modules/``. If ``BOXNAME`` is
    provided, creates the module inside ``modules/BOXNAME.``

    Use --interactive or -i to be prompted for module name.
    """
    if interactive or modulename is None:
        if modulename is None:
            modulename = click.prompt(
                " 📦 Enter module name",
                type=str,
                default="mymodule",
                show_default=True,
            )
        if boxname == "":
            add_to_box = click.confirm(
                " 📂 Do you want to add this module to a box?",
                default=False,
            )
            if add_to_box:
                boxname = click.prompt(
                    "    Enter box name",
                    type=str,
                    default="box__default",
                    show_default=True,
                )

    if boxname != "" and not boxname.startswith("box__"):
        click.secho(
            f" ❌ Error: Invalid BOXNAME '{boxname}'. It should start with 'box__' prefix.",
            fg="red",
            bold=True,
        )
        click.echo("    Example: box__ecommerce")
        sys.exit(1)

    if modulename.startswith("box_"):
        click.secho(
            f" ❌ Error: Invalid MODULENAME '{modulename}'. It cannot start with 'box_' prefix.",
            fg="red",
            bold=True,
        )
        sys.exit(1)

    if not is_alpha_num_underscore(modulename):
        click.secho(
            f" ❌ Error: MODULENAME '{modulename}' is not valid. Use alphanumeric and underscore only.",
            fg="red",
            bold=True,
        )
        sys.exit(1)

    if boxname != "" and not is_alpha_num_underscore(boxname):
        click.secho(
            f" ❌ Error: BOXNAME '{boxname}' is not valid. Use alphanumeric and underscore only.",
            fg="red",
            bold=True,
        )
        sys.exit(1)

    module_path = get_module_path_if_exists(modulename)

    if module_path is not None:
        click.secho(
            f" ❌ Error: Module '{modulename}' already exists at {module_path}",
            fg="red",
            bold=True,
        )
        sys.exit(1)

    if boxname != "":
        box_path = get_module_path_if_exists(boxname)
        if box_path is None:
            _create_box(boxname, verbose=verbose)

    module_path = os.path.join("modules", boxname, modulename)
    _create_module(modulename, base_path=module_path, verbose=verbose)


@cli.command("collectstatic", with_appcontext=False)
@click.argument("src", required=False, type=click.Path(), default="modules")
@click.option("--verbose", "-v", is_flag=True, default=False)
def collectstatic(src, verbose):
    """Copies ``static/`` in ``modules/`` or ``modules/SRC`` into
    ``/static/modules/``

    ``SRC`` is the module path relative to ``modules/`` where ``static/``
    exists.

    Ex usage for::

        \b
        .
        └── modules/
            └── box__default/
                ├── auth/
                │   └── static
                └── appadmin/
                    └── static

    To collect static in only one module, run either of two commands::

        $ shopyo collectstatic box__default/auth

        $ shopyo collectstatic modules/box__default/auth

    To collect static in all modules inside a box, run either of two commands
    below::

        $ shopyo collectstatic box__default

        $ shopyo collectstatic modules/box__default

    To collect static in all modules run either of the two commands below::

        $ shopyo collectstatic

        $ shopyo collectstatic modules
    """
    _collectstatic(target_module=src, verbose=verbose)


@cli.command("clean")
@click.option(
    "--clear-migration/--no-clear-migration",
    "clear_migration",
    "-cm",
    is_flag=True,
    default=True,
)
@click.option(
    "--clear-db/--no-clear-db", "clear_db", "-cdb", is_flag=True, default=True
)
@click.option("--verbose", "-v", is_flag=True, default=False)
def clean(verbose, clear_migration, clear_db):
    """removes ``__pycache__``, ``migrations/``, ``shopyo.db`` files and drops
    ``db`` if present
    """
    _clean(verbose=verbose, clear_migration=clear_migration, clear_db=clear_db)


@cli.command("initialise")
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option(
    "--clear-migration/--no-clear-migration",
    "clear_migration",
    "-cm",
    is_flag=True,
    default=True,
)
@click.option(
    "--clear-db/--no-clear-db", "clear_db", "-cdb", is_flag=True, default=True
)
@click.option("--verbose", "-v", is_flag=True, default=False)
@with_appcontext
def initialise(verbose, clear_migration, clear_db):
    import os

    if os.environ.get("SHOPYO_QUIET") == "True":
        verbose = False
    """
    Creates ``db``, ``migration/``, adds default users, add settings
    """
    if not os.path.exists("modules"):
        click.secho(
            " ❌ Error: 'modules' folder not found. Are you in the project root?",
            fg="red",
            bold=True,
        )
        click.secho(
            "    Try running 'shopyo new <project_name>' first.", fg="bright_black"
        )
        sys.exit(1)

    if os.environ.get("SHOPYO_QUIET") != "True":
        click.secho(" 🚀 Initializing project...\n", fg="cyan", bold=True)

    try:
        from flask import current_app

        db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
        click.secho(f" 🗄️  Using database: {db_uri}", fg="bright_black")
    except RuntimeError:
        pass

    # drop db, remove mirgration/ and shopyo.db
    _clean(verbose=verbose, clear_migration=clear_migration, clear_db=clear_db)

    # load all models available inside modules
    autoload_models(verbose=verbose)

    # add a migrations folder to your application.
    click.echo(" 📁 Creating database migrations...")
    if verbose:
        run(["flask", "db", "init"])
    else:
        run(["flask", "db", "init"], stdout=PIPE, stderr=PIPE)

    # load all models available inside modules
    autoload_models(verbose=verbose)
    click.echo(" ⚙️  Generating initial migration...")
    if verbose:
        run(["flask", "db", "migrate"])
    else:
        run(["flask", "db", "migrate"], stdout=PIPE, stderr=PIPE)

    click.echo(" ⬆️  Upgrading database...")
    if verbose:
        run(["flask", "db", "upgrade"])
    else:
        run(["flask", "db", "upgrade"], stdout=PIPE, stderr=PIPE)

    # collect all static folders inside modules/ and add it to global
    # static/
    _collectstatic(verbose=verbose)

    # Upload models data in upload.py files inside each module
    _upload_data(verbose=verbose)

    click.secho(
        "\n ✅ Initialization complete! Ready to develop.", fg="green", bold=True
    )
    click.echo("    Run 'flask run --debug' to start the server.\n")


@cli.command("new", with_appcontext=False)
@click.argument("projname", required=False, default="")
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option("--modules", "-m", is_flag=True, default=False)
@click.option(
    "--start",
    "-s",
    "start_server",
    is_flag=True,
    default=False,
    help="Auto-run initialise and start dev server",
)
@click.option(
    "--demo",
    "-d",
    is_flag=True,
    default=False,
    help="Create with demo modules and start server",
)
def new(projname, verbose, modules, start_server, demo):
    """Creates a new shopyo project.

    By default it will create the project(folder) of same name as the parent
    folder. If ``PROJNAME`` is provided, it will create ``PROJNAME/PROJNAME``
    under parent folder

    Use --start or -s to automatically run initialise and start the server
    Use --demo or -d to create with demo modules and start the server
    """

    modules_flag = modules

    if demo:
        modules = True
        start_server = True

    from shopyo import __version__
    from shopyo.api.file import trymkfile
    from shopyo.api.file import trymkdir
    from shopyo.api.cli_content import get_tox_ini_content
    from shopyo.api.cli_content import get_dev_req_content
    from shopyo.api.cli_content import get_gitignore_content
    from shopyo.api.cli_content import get_sphinx_conf_py
    from shopyo.api.cli_content import get_sphinx_makefile
    from shopyo.api.cli_content import get_index_rst_content
    from shopyo.api.cli_content import get_docs_rst_content
    from shopyo.api.cli_content import get_pytest_ini_content
    from shopyo.api.cli_content import get_manifest_ini_content
    from shopyo.api.cli_content import get_init_content
    from shopyo.api.cli_content import get_cli_content
    from shopyo.api.cli_content import get_setup_py_content

    here = os.getcwd()

    if projname == "":
        projname = os.path.basename(here)

        # the base/root project folder where files such as README, docs,
        # .gitignore etc. will be stored will be same as current working
        # directory i.e ./
        root_proj_path = here

        # the current project path in which we will create the project
        project_path = os.path.join(here, projname)

        if os.path.exists(project_path):
            click.echo(
                f"[ ] Error: Unable to create new project. Path {project_path} exits"
            )
            sys.exit(1)

    else:
        if not is_alpha_num_underscore(projname):
            click.echo(
                "[ ] Error: PROJNAME is not valid, please use alphanumeric "
                "and underscore only"
            )
            sys.exit(1)

        # the base/root project folder where files such as README, docs,
        # .gitignore etc. will be stored will be ./projname
        root_proj_path = os.path.join(here, projname)

        # the current project path in which we will create the project
        project_path = os.path.join(here, projname, projname)

        if os.path.exists(root_proj_path):
            click.echo(
                f"[ ] Error: Unable to create new project. Path {root_proj_path} exits"
            )
            sys.exit(1)

    click.echo(f"creating project {projname}...")
    click.echo(SEP_CHAR * SEP_NUM)

    # the shopyo src path that the new project will mimic
    src_shopyo_shopyo = Path(__file__).parent.parent.absolute()

    # copy the shopyo/shopyo content to the new project
    copytree(
        src_shopyo_shopyo,
        project_path,
        ignore=ignore_patterns(
            "__main__.py",
            "app.txt",
            "api",
            ".tox",
            ".coverage",
            "*.db",
            "coverage.xml",
            "setup.cfg",
            "instance",
            "migrations",
            "__pycache__",
            "*.pyc",
            "sphinx_source",
            "pyproject.toml",
            "modules",
            "static",
        ),
    )

    # create requirements.txt in root
    trymkfile(
        os.path.join(root_proj_path, "requirements.txt"),
        f"shopyo=={__version__}\n",
        verbose=verbose,
    )

    # copy the dev_requirement.txt in root
    trymkfile(
        os.path.join(root_proj_path, "dev_requirements.txt"),
        get_dev_req_content(),
        verbose=verbose,
    )

    # copy the tox.ini in root
    trymkfile(
        os.path.join(root_proj_path, "tox.ini"),
        get_tox_ini_content(projname),
        verbose=verbose,
    )

    # create MANIFEST.in needed for tox
    trymkfile(
        os.path.join(root_proj_path, "MANIFEST.in"),
        get_manifest_ini_content(projname),
        verbose=verbose,
    )

    # create README.md in root
    trymkfile(
        os.path.join(root_proj_path, "README.md"),
        f"# Welcome to {projname}",
        verbose=verbose,
    )

    # create .gitignore in root
    trymkfile(
        os.path.join(root_proj_path, ".gitignore"),
        get_gitignore_content(),
        verbose=verbose,
    )

    # create pytest.ini
    trymkfile(
        os.path.join(root_proj_path, "pytest.ini"),
        get_pytest_ini_content(),
        verbose=verbose,
    )

    # create setup.py
    trymkfile(
        os.path.join(root_proj_path, "setup.py"),
        get_setup_py_content(projname),
        verbose=verbose,
    )

    # override the __init__.py file
    trymkfile(
        os.path.join(project_path, "__init__.py"), get_init_content(), verbose=verbose
    )

    # add cli.py for users to add their own cli
    trymkfile(
        os.path.join(project_path, "cli.py"), get_cli_content(projname), verbose=verbose
    )

    sphinx_src = os.path.join(root_proj_path, "docs")

    # create sphinx docs in project root
    trymkdir(sphinx_src, verbose=verbose)
    # create sphinx conf.py inside docs
    trymkfile(
        os.path.join(sphinx_src, "conf.py"),
        get_sphinx_conf_py(projname),
        verbose=verbose,
    )
    # create _static sphinx folder
    trymkdir(os.path.join(sphinx_src, "_static"), verbose=verbose)
    trymkfile(os.path.join(sphinx_src, "_static", "custom.css"), "", verbose=verbose)
    # create sphinx Makefile inside docs
    trymkfile(
        os.path.join(sphinx_src, "Makefile"), get_sphinx_makefile(), verbose=verbose
    )
    # create index page
    trymkfile(
        os.path.join(sphinx_src, "index.rst"),
        get_index_rst_content(projname),
        verbose=verbose,
    )
    # create docs page
    trymkfile(
        os.path.join(sphinx_src, "docs.rst"),
        get_docs_rst_content(),
        verbose=verbose,
    )

    click.secho(
        f"\n ✨ Project '{projname}' created successfully!", fg="green", bold=True
    )
    click.echo(" " + "─" * 40)
    click.echo(" Next steps to get started:")
    if projname == "":
        click.secho(f"  1. cd {os.path.basename(os.getcwd())}", fg="cyan")
    else:
        click.secho(f"  1. cd {projname}/{projname}", fg="cyan")
    click.secho("  2. shopyo initialise (if you are using models)", fg="cyan")
    click.secho("  3. flask run --debug\n", fg="cyan")

    # Always copy static folder as it contains base assets (bootstrap, jquery etc)
    copytree(
        os.path.join(src_shopyo_shopyo, "static"),
        os.path.join(project_path, "static"),
    )

    if modules_flag:
        copytree(
            os.path.join(src_shopyo_shopyo, "modules"),
            os.path.join(project_path, "modules"),
        )
        tryrmtree(os.path.join(project_path, "modules", "tests"), verbose=verbose)
        tryrmtree(os.path.join(project_path, "modules", "box__tests"), verbose=verbose)
    else:
        # empty modules folder
        trymkdir(os.path.join(project_path, "modules"), verbose=verbose)

    if start_server:
        click.echo("\n 🚀 Starting server...")
        click.echo("    Press Ctrl+C to stop\n")

        if projname == "":
            project_dir = os.path.join(here, os.path.basename(here))
        else:
            project_dir = os.path.join(here, projname, projname)

        os.chdir(project_dir)

        os.environ["SHOPYO_CONFIG_PROFILE"] = "development"
        os.environ["FLASK_APP"] = "app.py"

        from shopyo.api.cmd import initialise as run_initialise
        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(run_initialise, [], obj={})

        if result.exit_code != 0:
            click.secho(f" ⚠️  Initialise warning: {result.output}", fg="yellow")
        else:
            click.secho(" ✅ Database initialized!", fg="green")

        _run_app("development")


@cli.command("rundebug", with_appcontext=False)
def rundebug():
    """runs the shopyo flask app in development mode"""
    _run_app("development")


@cli.command("runserver", with_appcontext=False)
def runserver():
    """runs the shopyo flask app in production mode"""
    _run_app("production")


@cli.command("env", with_appcontext=False)
@click.option(
    "--profile",
    "-p",
    default="development",
    type=click.Choice(["development", "production", "testing"]),
    help="Config profile to use",
)
def generate_env(profile):
    """Generate a .env file with required environment variables"""
    env_content = f"""# Shopyo Environment Configuration
# Generated by shopyo

# Flask configuration
FLASK_APP=app.py
FLASK_DEBUG=1
SHOPYO_CONFIG_PROFILE={profile}
ENV={profile}

# Database (SQLite by default)
# DATABASE_URL=sqlite:///shopyo.db

# Secret key (change this in production!)
SECRET_KEY=dev-secret-key-change-in-production

# Optional: Email configuration
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=true
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-password
"""

    if os.path.exists(".env"):
        if not click.confirm(" ⚠️  .env already exists. Overwrite?"):
            click.echo("Aborted.")
            return

    with open(".env", "w") as f:
        f.write(env_content)

    click.secho(" ✅ .env file created!", fg="green", bold=True)
    click.echo("    You can now run: flask run --debug")


@cli.command("audit", with_appcontext=False)
@click.option("warning", "--show-warning", is_flag=True, default=False)
@click.option("info", "--show-info", is_flag=True, default=False)
@click.option("severe", "--show-severe", is_flag=True, default=False)
def audit(warning, info, severe):
    """Audits the project and finds issues"""
    if not (warning or info or severe):
        warning, info, severe = not warning, not info, not severe
    _audit(warning, info, severe)


@cli.command("rename", with_appcontext=False)
@click.argument("old_name", required=True)
@click.argument("new_name", required=True)
@click.option("--verbose", "-v", is_flag=True, default=False)
def rename(old_name, new_name, verbose):
    """Renames apps"""
    _rename_app(old_name, new_name)


@cli.command("testok", with_appcontext=False)
def testok():
    """Just testing if the cli works"""
    click.echo("test ok!")


if __name__ == "__main__":
    cli()
