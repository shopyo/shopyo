# Shopyo Theme

The `shopyo_theme` package provides a theme management system for Shopyo applications. It supports both **plain themes** (statically bundled in `static/themes/`) and **package-based themes** (distributed as Python packages with namespaced names like `shopyo_theme/mistrello`).

## Features

- **Dual theme tracks** — separate Front (public) and Back (admin) themes
- **Namespaced themes** — serve CSS/assets from any Flask blueprint's `static/themes/` directory
- **Metadata support** — `info.json` with author, version, description
- **Config-first defaults** — config takes priority over DB, so themes work without a populated database
- **Visual interface** — activate themes from the admin dashboard

## Theme types

### Plain themes (`static/themes/`)

```text
static/
└── themes/
    ├── front/
    │   └── my_theme/
    │       ├── info.json
    │       └── styles.css
    └── back/
        └── my_admin_theme/
            ├── info.json
            └── styles.css
```

Activate by setting the DB entry `ACTIVE_FRONT_THEME = "my_theme"`.

### Package-based themes (`blueprint/static/themes/`)

Themes distributed as Python packages. The blueprint must have `static_folder="static"`:

```text
shopyo_theme/
├── __init__.py          # blueprint registered with static_folder="static"
└── static/
    └── themes/
        ├── front/
        │   └── blogus/
        │       ├── info.json
        │       └── styles.css
        └── back/
            └── mistrello/
                ├── info.json
                └── styles.css
```

Activate using the namespaced name: `ACTIVE_FRONT_THEME = "shopyo_theme/blogus"`.

The system resolves `shopyo_theme/blogus` by:
1. Splitting on `/` → blueprint name `shopyo_theme`, theme dir name `blogus`
2. Looking up the Flask blueprint to get its `root_path`
3. Joining `root_path/static/themes/front/blogus/`

### `info.json`

```json
{
    "author": {
        "name": "Your Name",
        "email": "your@email.com"
    },
    "version": "1.0.0",
    "display_name": "My Theme"
}
```

## Configuration

| Key | Default | Description |
|-----|---------|-------------|
| `SHOPYO_THEME_FRONT_DEFAULT` | `shopyo_theme/blogus` | Fallback front theme |
| `SHOPYO_THEME_BACK_DEFAULT` | `shopyo_theme/mistrello` | Fallback back theme |
| `SHOPYO_THEME_DEFAULT` | `shopyo_theme/blogus` | Legacy fallback for front |
| `SHOPYO_THEME_URL` | `/shopyo-theme` | Blueprint URL prefix |

Resolution order: config default → DB setting (`ACTIVE_FRONT_THEME` / `ACTIVE_BACK_THEME`).

## Packaging a theme

To distribute a theme as a pip package:

1. Create a Python package with a Flask blueprint that has `static_folder="static"`
2. Place themes under `static/themes/{front|back}/{name}/`
3. Add `info.json` to each theme directory
4. In `pyproject.toml`:
   ```toml
   [tool.setuptools.package-data]
   shopyo_theme = ["static/**", "templates/**", "*.json"]
   ```

## Testing

```bash
cd tests/testapp
python -m pytest tests/ -v
```

The testapp is a minimal Shopyo project that initialises `ShopyoTheme` and exercises config values, blueprint registration, `_get_blueprint_theme_dir` resolution, theme directory lookups, CSS URL generation, and HTTP CSS serving.
