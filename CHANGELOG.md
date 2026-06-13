## v4.18.1 (2026-06-13)

- 🔧 Auto-copy default themes from `shopyo` package when missing
- 🔧 `get_folders` handles missing paths gracefully; fallback for `plugin_folder_path`
- 🔧 Fixed static file serving in production deployments

## v4.18.0 (2026-05-28)

- ✨ Fixed dead auth guard in admin panel; proper unauthenticated redirect + 403
- ✨ Enforce environment-only secrets; `RuntimeError` if `SECRET_KEY` or `SQLALCHEMY_DATABASE_URI` unset
- ✨ Hardened session cookies with `HttpOnly`, `SameSite=Lax`, `Secure` in production
- ✨ Development secret key warning with `DeprecationWarning`
- ✨ Seed admin defaults removed; seeding skipped when both email and password unset
- ✨ API token hashing upgraded to `pbkdf2_hmac` with per-token 32-byte random salt
- ✨ Rate limiting enabled by default with endpoint-specific limits
- ✨ Password complexity enabled by default with minimum length enforcement
- ✨ Unified CSRF protection via Flask-WTF `CSRFProtect`
- 🎉 Policy-based authorization engine with `Permission` enum, `Policy` dataclass, and `PolicyEngine`
- 🎉 Persistent login support with `SHOPYO_AUTH_REMEMBER_COOKIE_DURATION`
- 🎉 Customizable login and registration templates
- 🎉 Improved dev UX with better errors, interactive CLI, and colored output
- 🎉 Single-command project creation with `--demo` flag and `.env` generation
- 🖌️ Bundled Tailwind CSS, AlpineJS, and FontAwesome 6.5.1 locally
- 🎉 Enhanced Page Module with per-page custom templates and `SHOPYO_PAGE_TEMPLATE`
- 🖌️ Revamped `shopyo-page` and `shopyo-dashboard` with modern Tailwind aesthetic
- 🔧 Improved plugin asset serving and auto-discovery in `collectstatic`
- 🔧 Page module fixes: custom template saving, missing language field, 404 for missing pages
- 🔧 `shopyo new` works in existing directories; conditional `cd` instruction
- 🔧 Robust CLI via `sys.executable -m flask`
- 🔧 Dashboard UI: consistent buttons, icons, improved aesthetics, working CRUD flows
- 🔧 Static serving: theme loading, `shopyo-theme` URL, upload path
- 🔧 Auth fixes: syntax errors in forms.py, NameError in view.py, admin panel auth bug
- 🔧 Replaced TinyMCE with Quill rich text editor
- 🔧 Test coverage increased to 75%

## v4.17.0 (2026-03-11)

- 🔥 Zero-Friction Static Assets with Transparent Static Shadowing
- 🎉 Flattened project scaffolding eliminating `proj/proj` nesting
- 🖌️ Bundled Tailwind CSS, AlpineJS, and FontAwesome 6.5.1 locally
- 🎉 Enhanced Page Module with per-page custom templates and `SHOPYO_PAGE_TEMPLATE`
- 🖌️ Revamped `shopyo-page` and `shopyo-dashboard` with modern Tailwind aesthetic
- 🎉 Support SQLAlchemy 2.0
- 🔧 Core Module Logic: `static_folder` support in `ModuleHelp`
- 🔧 Updated `shopyo new` templates for flat directory structure
- 🔧 Cleaned up unused legacy assets
- 🔧 Removed `config.json` in favor of standard `config.py`
- 🔧 Corrected `shopyo_theme` endpoints to fix `BuildError`
- 🔧 Improved `shopyo-page` public rendering with functional language switcher
- 🔧 Removed broken/unused revisions links from dashboard
- 🔧 Auth functional tests redirect assertions
- 🔧 Database seeding in tests (IntegrityError)

## v4.15.0 (2026-01-06)

- 🎉 Modernized CLI output with colors, emojis, and better guidance
- 🎉 `startapp` scaffolds `forms.py` and `models.py` with standard imports
- 🎉 Improved CLI instructions recommending `flask run --debug`
- 🎉 Added `__repr__` to `PkModel`
- 🎉 Added polls demo app
- 🔧 Add `exp/` to `.gitignore`
- 🔧 Tone down complexity in app.py

## v4.14.0 (2026-01-06)

- 🎉 Auth updates and improvements
- 🎉 Added demo apps

## v4.13.1 (2026-01-01)

- 🔧 Fixed readthedocs configuration and build
- 🔧 Update tests and remove CodeQL CI

## v4.13.0 (2026-01-01)

- 🎉 Basic endpoint and response functionalities
- 🎉 Improved models, security, and templates utilities
- 🔧 CI/CD compatibility and test stability
- 🔧 Windows CI and import errors
- 🔧 Models fixes
- 🔧 Updated tests and CI configuration
- 🔧 Pre-commit auto fixes

## 4.12.1 (2024-10-11)

- 🎉 Options to override default URL for default packages
- 🎉 Options added to appadmin, auth, i18n, page, and theme packages
- 🎉 `get_pages` utility
- 🎉 Migrated resource module endpoints to theme
- 🎉 Removed resource module
- 🔧 Explicit error message on import errors
- 🔧 `set_setting` updates setting if exists, else creates
- 🔧 Support up to Python 3.13

## 4.12.0 (2024-10-03)

- 🔧 Version bump and package updates

## 4.11.1 (2024-10-05)

- 🎉 Converted page module to `shopyo_page` package
- 🎉 Dashboard package fetches plugins from `current_app.extensions`
- 🎉 `get_info()` for packages
- 🎉 `shopyo-seed` CLI command
- 🎉 Extracted i18n into its own package
- 🔧 Moved settings and theme to default packages
- 🔧 Explicit upload feedback

## 4.11.0 (2024-09-28)

- 🎉 Extracted appadmin, auth, dashboard as separate packages
- 🔧 Adjusted package references across the codebase

## 4.10.0 (2024-09-27)

- 🎉 `shopyo_base` base module package
- 🔧 CLI cleanup and refactoring
- 🔧 Readthedocs YAML configuration updates

## 4.9.5 (2024-04-07)

- 🎉 Support SQLAlchemy 2.0

## 4.9.4 (2024-04-04)

- 🔧 Version bump and package updates

## v4.8.3 (2023-01-13)

- 🎉 i18n support
- 🎉 Filtering options for audit command
- 🔧 CodeQL analysis workflow and scorecard
- 🔧 Security alert fixes
- 🔧 Dashboard access restricted to non-admin users
- 🔧 Print module load errors

## v4.6.0 (2022-08-30)

- 🎉 Plugin basics and complete package addition
- 🎉 Module functionalities extended for packages
- 🎉 Load extensions in `__init__`
- 🔧 Move register devstatic API
- 🔧 Upload key fix
- 🔧 Empty static handling

## v4.5.2 (2022-04-16)

- 🎉 URL conflict detection in audit command
- 🔧 Serving static assets via `api.assets.get_static`
- 🔧 `get_static` path fixed (not from templates)
- 🔧 Re-enabled CLI integration tests
- 🔧 Increased test coverage

## v4.4.3 (2022-04-12)

- 🔧 Fix readthedocs Sphinx version
- 🔧 Fix email-validator version pinning
- 🔧 Fix `initialise` command failing

## v4.4.1 (2022-04-11)

- 🎉 Rename command for boxes and apps
- 🎉 Better audit command
- 🔧 Load global configs
- 🔧 Removed db-dependent function for default www page
- 🔧 Removed Python 3.6 support
- 🔧 Adjusted audit warning levels

## v4.3.2 (2022-04-09)

- 🎉 `shopyo audit` command
- 🔧 Refactored assets folder
- 🔧 Clean box default
- 🔧 Moved email from auth to API
- 🔧 Fixed severe audit warnings

## v4.2.0 (2021-11-24)

- 🔧 Release fixes

## v4.1.3 (2021-10-26)

- 🔧 Pin exact version when creating new project
- 🔧 Various bug fixes

## v3.9.0 (2021-03-01)

- 🎉 Click-based CLI replacing argv parsing
- 🎉 `startbox2` command
- 🎉 `is_valid_url` validator
- 🔧 Path bug fixes
- 🔧 Removed config.py from .gitignore

## v3.3.6 (2021-01-09)

- 🎉 Announcement module with CRUD
- 🎉 CRUD helper class for admin models
- 🔧 Replaced pycodestyle with flake8
- 🔧 Scrolling fix for long content
- 🔧 Updated test and docs configuration

## v3.0.0 (2020-12-22)

- 🎉 Disabled autoblack
- 🔧 Added `tox` for testing
- 🔧 Migration from Python 3.5
- 🔧 Functional tests for admin and contact modules
- 🔧 Marshmallow_sqlalchemy fix for Python 3.5

## v2.0.0 (2020-11-03)

- 🎉 Theme versioning
- 🎉 Product pictures with unique filename and upload
- 🎉 Replaced Flask-Script by Click
- 🔧 Login required for all pages
- 🛩️ Docker support

## v1.2.4 (2020-10-09)

- 🔧 LGTM error fixes
- 🔧 Travis CI configuration

## v1.2.0 (2020-03-29)

- 🎉 Control panel basic demo with modules info
- 🎉 Auto-load modules and view.py convention

## v1.1.7 (2020-10-04)

- 🎉 Page module completed
- 🎉 Validators added to `shopyoapi`
- 🔧 Changes to `info.json`

## v1.1.0 (2020-03-19)

- 🎉 Django-like structure
- 🎉 Active page support
- 🎉 Product addition and subnav for manufacturer/products
- 🔧 Unit tests set up
- 🔧 Sphinx docs added

## 1.0.0 (2020-03-08)

- 🎉 Initial release with module architecture and base as blueprint
