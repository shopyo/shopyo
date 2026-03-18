# Shopyo Skill

Shopyo is a modular Flask framework designed for maintainability, extensibility, and real-world scale.

## Project Structure

A typical Shopyo project:

```
/project_root
├── app.py          # Entry point, defines create_app()
├── init.py         # Extension initializer (db, login_manager, etc.)
├── manage.py       # CLI entry point
├── config.py       # Profile-based configuration
└── modules/        # Modular code
    ├── box__default/
    │   ├── auth/
    │   └── settings/
    └── my_custom_module/
```

## CLI Commands

```bash
# Environment setup
export SHOPYO_CONFIG_PROFILE=development
export FLASK_ENV=development
export FLASK_APP=app.py

# New project
shopyo new myproject --demo
cd myproject
shopyo initialise

# Create module
shopyo startapp modulename [boxname]

# Create box
shopyo startbox box__name

# Run server
shopyo run
flask run --debug

# Database
shopyo initialise   # Fresh start (creates db, migrations, default users)
shopyo db migrate
shopyo db upgrade
shopyo clean        # Reset local database

# Static files
shopyo collectstatic [module_path]  # Collect static files from modules

# Other
shopyo routes       # Show all routes
shopyo audit        # Find project issues
shopyo rename old_name new_name  # Rename module
```

## Creating a Module

```bash
shopyo startapp blog
# or with box
shopyo startapp blog box__ecommerce
```

Creates:

```
modules/blog/
├── __init__.py
├── forms.py
├── global.py
├── info.json
├── models.py
├── view.py
├── static/
├── templates/
│   └── blog/
│       ├── blocks/
│       │   └── sidebar.html
│       ├── dashboard.html
│       └── index.html
└── tests/
    ├── test_blog_functional.py
    └── test_blog_models.py
```

## info.json Structure

```json
{
   "author": {"mail": "", "name": "", "website": ""},
   "display_string": "Page",
   "module_name": "page",
   "type": "show",
   "fa-icon": "fa fa-store",
   "url_prefix": "/page",
   "dashboard": "/dashboard"
}
```

## Module View Pattern

```python
from shopyo.api.module import ModuleHelp

mhelp = ModuleHelp(__file__, __name__)
blueprint = mhelp.blueprint

@blueprint.route("/")
def index():
    context = mhelp.context()
    context.update({'message': 'Hello'})
    return mhelp.render('index.html', **context)
```

## Models Pattern

```python
from init import db
from shopyo.api.models import PkModel

class MyModel(PkModel):
    __tablename__ = 'mymodel'
    name = db.Column(db.String(100))
```

## Templates

Extend the base template:

```html
{% extends "shopyo_base/main_base.html" %}
{% block content %}
<h1>Hello</h1>
{% endblock %}
```

Use `yo_render`:

```python
from shopyo.api.templates import yo_render

@blueprint.route("/demo")
def demo():
    return yo_render('blog/demo.html', {'key': 'value'})
```

## Shopyo API

Key imports:

```python
from shopyo.api.module import ModuleHelp, get_module, dispatch
from shopyo.api.models import PkModel
from shopyo.api.templates import yo_render
from shopyo.api.database import db
from shopyo.api.enhance import enhance_html
```

## Inter-Module Communication

Use the event system:

```python
from shopyo.api.module import dispatch

# Dispatch event
dispatch("user:registered", {"email": user.email})

# Listen for event
@dispatch("user:registered")
def send_welcome_email(email):
    pass
```

## Testing

```bash
pytest
pytest -v
pytest path/to/test.py
pytest --cov=shopyo
tox
```

## Global.py Pattern

```python
available_everywhere = {"x": 1}

configs = {
    "development": {"CONFIG_VAR": "DEVVALUE"},
    "production": {"CONFIG_VAR": "PRODVALUE"},
    "testing": {"CONFIG_VAR": "TESTVALUE"}
}
```

## Default Credentials

After `shopyo initialise`:
- URL: http://localhost:5000
- Login: http://localhost:5000/auth/login
- Email: `admin@domain.com`
- Password: `pass`

## Key Conventions

- Box folders must start with `box__`
- Modules are isolated - do not import between modules directly
- Use event system (`dispatch`) for inter-module communication
- Run `shopyo initialise` after adding/removing modules
- Static files are collected into `static/modules/` - don't edit directly
- Use `shopyo clean` to reset local development database
