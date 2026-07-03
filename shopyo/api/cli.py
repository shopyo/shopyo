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

from shopyo.api.cli_output import cli_error
from shopyo.api.cli_output import cli_info
from shopyo.api.cli_output import cli_step
from shopyo.api.cli_output import cli_success
from shopyo.api.cli_output import cli_warning
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
        error_msg = str(e)
        if error_msg.startswith("No module named 'app'"):
            cli_error(
                error_msg,
                hint="Make sure you are in your Shopyo project root directory.\n"
                "    Your project should have an 'app.py' file with a 'create_app' function.",
            )
        cli_error(error_msg)
    except AttributeError as e:
        cli_error(
            "Could not find 'create_app' in 'app.py'.",
            hint=f"Details: {e}\n"
            "    Your 'app.py' should define a 'create_app(config_name)' function.\n"
            "    Example:\n"
            "        def create_app(config_name='development'):\n"
            "            app = Flask(__name__)\n"
            "            # ... initialize extensions and modules\n"
            "            return app",
        )

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
            cli_warning("Box name should start with 'box__' prefix. Adding automatically...")
            boxname = "box__" + boxname

    path = os.path.join("modules", boxname)

    if os.path.exists(os.path.join("modules", boxname)):
        cli_error(f"Box '{path}' already exists!")

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
        cli_error(
            f"Invalid BOXNAME '{boxname}'. It should start with 'box__' prefix.",
            hint="Example: box__billing",
        )

    if modulename.startswith("box_"):
        cli_error(
            f"Invalid MODULENAME '{modulename}'. It cannot start with 'box_' prefix."
        )

    if not is_alpha_num_underscore(modulename):
        cli_error(
            f"MODULENAME '{modulename}' is not valid. Use alphanumeric and underscore only."
        )

    if boxname != "" and not is_alpha_num_underscore(boxname):
        cli_error(
            f"BOXNAME '{boxname}' is not valid. Use alphanumeric and underscore only."
        )

    module_path = get_module_path_if_exists(modulename)

    if module_path is not None:
        cli_error(f"Module '{modulename}' already exists at {module_path}")

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
@click.option(
    "--yes",
    "-y",
    "force",
    is_flag=True,
    default=False,
    help="Skip confirmation prompts",
)
@click.option(
    "--db-only",
    is_flag=True,
    default=False,
    help="Only run database steps (migrate + upgrade)",
)
@click.option(
    "--static-only",
    is_flag=True,
    default=False,
    help="Only collect static assets",
)
@click.option(
    "--seed-only",
    is_flag=True,
    default=False,
    help="Only seed database data",
)
@with_appcontext
def initialise(verbose, clear_migration, clear_db, force, db_only, static_only, seed_only):
    """
    Creates ``db``, ``migration/``, adds default users, add settings
    """
    import os

    if os.environ.get("SHOPYO_QUIET") == "True":
        verbose = False

    exclusive_flags = [db_only, static_only, seed_only]
    if sum(exclusive_flags) > 1:
        cli_error(
            "Only one of --db-only, --static-only, --seed-only can be used at a time."
        )

    if not os.path.exists("modules"):
        cli_error(
            "'modules' folder not found. Are you in the project root?",
            hint="Try running 'shopyo new <project_name>' first.",
        )

    if not force and not any(exclusive_flags):
        click.secho(
            " 🚀 This will reset your database and migrations. Continue?",
            fg="yellow",
            bold=True,
        )
        click.confirm("    Proceed?", default=False, abort=True)

    if os.environ.get("SHOPYO_QUIET") != "True":
        click.secho(" 🚀 Initializing project...\n", fg="cyan", bold=True)

    try:
        from flask import current_app

        db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
        cli_info(f"Using database: {db_uri}")
    except RuntimeError:
        pass

    if seed_only:
        _upload_data(verbose=verbose)
        cli_success("Database seeded successfully!")
        return

    if static_only:
        _collectstatic(verbose=verbose)
        cli_success("Static assets collected successfully!")
        return

    # drop db, remove migrations/ and shopyo.db
    _clean(verbose=verbose, clear_migration=clear_migration, clear_db=clear_db)

    if db_only:
        cli_info("Skipping static collection and data seeding (--db-only)")

    # load all models available inside modules
    autoload_models(verbose=verbose)

    # add a migrations folder to your application.
    cli_step("Creating database migrations...")
    flask_cmd = [sys.executable, "-m", "flask"]
    if verbose:
        run(flask_cmd + ["db", "init"])
    else:
        run(flask_cmd + ["db", "init"], stdout=PIPE, stderr=PIPE)

    # load all models available inside modules
    autoload_models(verbose=verbose)
    cli_step("Generating initial migration...")
    if verbose:
        run(flask_cmd + ["db", "migrate"])
    else:
        run(flask_cmd + ["db", "migrate"], stdout=PIPE, stderr=PIPE)

    cli_step("Upgrading database...")
    if verbose:
        run(flask_cmd + ["db", "upgrade"])
    else:
        run(flask_cmd + ["db", "upgrade"], stdout=PIPE, stderr=PIPE)

    if not db_only:
        # collect all static folders inside modules/ and add it to global
        # static/
        _collectstatic(verbose=verbose)

        # Upload models data in upload.py files inside each module
        _upload_data(verbose=verbose)

    cli_success("Initialization complete! Ready to develop.")
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
        root_proj_path = here
        project_path = here
    else:
        if not is_alpha_num_underscore(projname):
            cli_error(
                "PROJNAME is not valid, please use alphanumeric and underscore only."
            )

        root_proj_path = os.path.join(here, projname)
        project_path = root_proj_path

        if os.path.exists(project_path):
            cli_error("Unable to create new project, directory already exists.")

    click.echo(f"creating project {projname}...")
    click.echo(SEP_CHAR * SEP_NUM)

    # the shopyo src path that the new project will mimic
    src_shopyo_shopyo = Path(__file__).parent.parent.absolute()

    # copy the shopyo/shopyo content to the new project
    copytree(
        src_shopyo_shopyo,
        project_path,
        dirs_exist_ok=True,
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
            "cli.py",
            "__init__.py",
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
    step = 1
    if projname != os.path.basename(here) or project_path != here:
        click.secho(f"  {step}. cd {projname}", fg="cyan")
        step += 1
    click.secho(f"  {step}. shopyo initialise (if you are using models)", fg="cyan")
    step += 1
    click.secho(f"  {step}. flask run --debug\n", fg="cyan")

    # Always copy static folder as it contains base assets (bootstrap, jquery etc)
    copytree(
        os.path.join(src_shopyo_shopyo, "static"),
        os.path.join(project_path, "static"),
        dirs_exist_ok=True,
    )

    if modules_flag:
        copytree(
            os.path.join(src_shopyo_shopyo, "modules"),
            os.path.join(project_path, "modules"),
            dirs_exist_ok=True,
        )
        tryrmtree(os.path.join(project_path, "modules", "tests"), verbose=verbose)
        tryrmtree(os.path.join(project_path, "modules", "box__tests"), verbose=verbose)
    else:
        # empty modules folder
        trymkdir(os.path.join(project_path, "modules"), verbose=verbose)

    if start_server:
        click.echo("\n 🚀 Starting server...")
        click.echo("    Press Ctrl+C to stop\n")

        project_dir = project_path

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
