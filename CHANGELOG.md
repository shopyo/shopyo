## Unreleased

### Security

- **Enforce environment-only secrets:** `ProductionConfig` now raises `RuntimeError` if `SECRET_KEY` or `SQLALCHEMY_DATABASE_URI` are not set via environment variables. `PASSWORD_SALT` defaults to a random 64-char hex if not provided.
- **Hardened session cookies:** `BaseConfig` now sets `SESSION_COOKIE_HTTPONLY = True` and `SESSION_COOKIE_SAMESITE = "Lax"`. `ProductionConfig` additionally sets `SESSION_COOKIE_SECURE = True`.
- **Development secret key warning:** `DevelopmentConfig` emits a `DeprecationWarning` when `SECRET_KEY` is unset or uses the default `"secret"` value.
- **Seed admin defaults removed:** `SHOPYO_AUTH_SEED_ADMIN_EMAIL` and `SHOPYO_AUTH_SEED_ADMIN_PASSWORD` default to `None`. Seeding is skipped when both are unset.
- **Fixed dead auth guard:** `MyAdminIndexView.index()` no longer uses the unreachable `not current_user.is_authenticated and current_user.is_admin` condition. Unauthenticated users are redirected to login; unauthorized users get 403.
- **Policy Engine:** Added `shopyo.api.perms` with `Permission` enum, `Policy` dataclass, and `PolicyEngine` for replacing `is_admin` checks.

## v4.17.0 (2026-03-11)

### Feat

- **Zero-Friction Static Assets:** Implemented Transparent Static Shadowing. Developers can now use standard Flask `url_for('static', filename='modules/...')` calls which resolve dynamically in development and physically in production.
- **Flattened Project Scaffolding:** `shopyo new` now creates a flat, standard project structure, eliminating the confusing `proj/proj` nesting trap.
- **Modernized Dashboard Assets:** Bundled Tailwind CSS, AlpineJS, and FontAwesome 6.5.1 locally into the `shopyo-dashboard` package for offline reliability.
- **Enhanced Page Module:** Added support for per-page custom templates and a global `SHOPYO_PAGE_TEMPLATE` configuration.
- **Modern UI:** Revamped `shopyo-page` and `shopyo-dashboard` admin interfaces with a modern Tailwind-based aesthetic.
- Support SQLAlchemy 2.0.

### Refactor

- **Core Module Logic:** Enabled `static_folder` support in the `ModuleHelp` class for automated blueprint asset management.
- **Project Scaffolding:** Updated `shopyo new` templates (`setup.py`, `manifest.in`, `tox.ini`) to support the new flat directory structure.
- Cleaned up unused legacy assets from the core `shopyo` package.
- Removed `config.json` mechanism in favor of standard `config.py` variables.

### Fix

- Corrected `shopyo_theme` helper endpoints to fix `BuildError`.
- Improved `shopyo-page` public rendering by removing demo text and adding a functional language switcher.
- Removed broken/unused revisions links from the dashboard UI.
- Auth functional tests redirect assertions.
- Database seeding in tests (IntegrityError).

### Docs

- Major documentation overhaul: updated `README.md`, `quickstart.rst`, and `assets.rst` to reflect the new Shopyo 2.0 workflows.
- Added comprehensive `README.md` for `shopyo-page`.
- New internal audit report: `oss-report.md`.

## v4.13.1 (2026-01-01)

### Fix

- docs and readthedocs configuration (#220)

### Chore

- update tests and remove codeql ci

## v4.13.0 (2026-01-01)

### Fix

- windows failing tests

### Chore

- auto fixes from pre-commit

## 4.9.4 (2024-04-04)
...
