<p align="center">
  <a href="https://github.com/shopyo/shopyo"><img src="https://github.com/shopyo/shopyo/blob/dev/assets/github_banner.png" alt="shopyo" width=""></a>
</p>

<p align="center">
  <b>Build large Flask apps without losing your sanity.</b><br>
  Auth, admin panel, modular architecture — all the batteries, none of the boilerplate.
</p>

<p align="center">
  <a href="https://pepy.tech/project/shopyo"><img src="https://static.pepy.tech/badge/shopyo/month" alt="Downloads"></a>
  <a href="https://codecov.io/gh/shopyo/shopyo"><img src="https://codecov.io/gh/shopyo/shopyo/branch/dev/graph/badge.svg?token=J4TL2MDTSS" alt="Codecov"></a>
  <a href="https://github.com/shopyo/shopyo/actions/workflows/tests.yaml"><img src="https://github.com/shopyo/shopyo/actions/workflows/tests.yaml/badge.svg" alt="Tests"></a>
  <a href="https://pypi.python.org/pypi/shopyo/"><img src="https://img.shields.io/pypi/v/shopyo.svg" alt="PyPI"></a>
  <a href="https://shopyo.readthedocs.io/en/latest/"><img src="https://readthedocs.org/projects/shopyo/badge/?version=latest" alt="Docs"></a>
  <a href="https://bestpractices.coreinfrastructure.org/projects/5350"><img src="https://bestpractices.coreinfrastructure.org/projects/5350/badge" alt="CII"></a>
  <a href="https://api.securityscorecards.dev/projects/github.com/shopyo/shopyo"><img src="https://api.securityscorecards.dev/projects/github.com/shopyo/shopyo/badge" alt="OpenSSF"></a>
</p>

<p align="center">
  <a href="https://shopyo.readthedocs.io/en/latest/">📖 Docs</a> •
  <a href="https://discord.gg/k37Ef6w">💬 Discord</a> •
  <a href="https://shopyo.readthedocs.io/en/latest/contrib.html">🎯 Contribute</a> •
  <a href="https://twitter.com/shopyoproject">🐦 Twitter</a>
</p>

---

**Your Flask app works. Until it doesn't.**

You start with a single `app.py`. Then you add auth. Then an admin panel. Then a few blueprints. Suddenly you have 5,000 lines and no idea where anything lives. You think about Django — but you chose Flask for a reason.

Shopyo is the answer. It gives you the **modular architecture**, **auth**, **admin dashboard**, **CLI scaffolding**, and **project structure** that Flask is missing — in one `pip install`.

```bash
pip install shopyo
shopyo new myapp
cd myapp && shopyo initialise && flask run --debug
# → Working app with auth, admin panel, and dashboard at localhost:5000
```

Featured on [Python Weekly issue 436](https://newsletry.com/Home/Python%20Weekly/9a578693-14ba-47c5-8a8e-08d7b0139fe7) and presented at [EuroPython 2023](https://youtu.be/rkzXQOC1T0Q).

---

## Why Shopyo?

| Instead of this... | You get this |
|---|---|
| Wiring up Flask-Login, Flask-Admin, Flask-Migrate, Flask-WTF, and 5 other extensions separately | One `pip install` with everything working together |
| Manually registering blueprints and hoping you didn't miss one | Auto-discovery: drop a module in `modules/` and it just works |
| Googling "how to structure a large Flask app" for the 10th time | A proven architecture that scales from day one |
| Configuring static files differently for dev and prod | Zero-friction assets: one `url_for()` call works everywhere |
| Writing the same user management UI for every project | Built-in admin dashboard and user management |

## Features

- **🔐 Auth built-in** — Login, registration, password reset, email confirmation, API tokens, rate limiting, password complexity, roles, and an events system. Drop-in, no wiring required.
- **📦 2-level modularity** — Organize features as **modules** and group them into **boxes**. Add, remove, or replace parts without touching the rest of your app.
- **🖥️ Admin dashboard** — User management, settings, and a customizable admin panel. Works out of the box, fully hackable.
- **🪜 CLI scaffolding** — `shopyo new` creates a project. `shopyo startapp` creates a module. `shopyo startbox` creates a box. No boilerplate to write.
- **🌅 Zero-friction assets** — Use standard Flask `url_for('static', ...)` in development and production. Transparent static shadowing handles the rest.
- **⚛️ i18n ready** — Internationalization setup included.
- **🎨 Theme system** — Front-end and back-end theming with pluggable CSS themes.
- **🔧 Production-ready** — Session hardening, CSRF protection, environment-enforced secrets, rate limiting, multi-platform CI/CD, 75%+ test coverage.
- **🔑 Policy-based authorization** — Role-based access control with fine-grained permissions, grant/revoke semantics, and a `require` decorator for protecting views.
- **🔄 Persistent login** — Optional "remember me" functionality with configurable cookie duration.
- **📝 Customizable auth pages** — Override login and registration templates via config without touching package internals.
- **🧩 Modular packages** — Auth, dashboard, page, i18n, settings, theme, and appadmin extracted as independent packages with URL override support.
- **⚡ Modern UI** — Tailwind CSS, AlpineJS, and FontAwesome 6.5.1 bundled locally for offline reliability.
- **🖊️ Rich text editing** — Quill editor integrated for a lightweight writing experience.
- **🎯 Demo scaffolding** — `shopyo new --demo` creates a project pre-loaded with demo apps.

## Quick start

```bash
pip install shopyo
shopyo new blog
cd blog
shopyo initialise
flask run --debug
```

Open http://localhost:5000/dashboard — credentials: `admin@domain.com` / `pass`.

> You can also run `shopyo new` inside an existing directory to scaffold Shopyo in place.
> Note: `shopyo new .` does **not** work — the project name must be alphanumeric.
> Use `shopyo new` (no argument) instead to create the project in the current directory.

## What does "modular" mean?

Every feature in Shopyo is a **module**. Modules are self-contained Flask blueprints with their own models, views, forms, templates, and static assets.

```
myproject/
├── modules/
│   ├── www/              # Homepage, public routes
│   ├── blog/             # Blog module (you create this)
│   ├── analytics/        # Analytics module (you create this)
│   └── box__billing/     # Box: group of related modules
│       ├── subscriptions/
│       └── invoices/
├── config.py
├── app.py
└── requirements.txt
```

Add a module by dropping a folder into `modules/`. Shopyo auto-discovers and registers it. No blueprint registration, no configuration files to update.

## Who uses Shopyo?

| Site | Description |
|---|---|
| [Maurilearn.com](https://maurilearn.com) | Elearning platform |
| [Linkolearn.com](https://linkolearn.com) | Learn by links |
| [FlaskCon.com](https://flaskcon.com) | Conference software |

**Built something with Shopyo?** [Let us know](https://github.com/shopyo/shopyo/discussions) and we'll add you to the list.

## Why not Django?

Django is excellent for Django-shaped problems. But if you want:
- Flask's **flexibility** (swap SQLAlchemy for Peewee, Jinja for Mako)
- A **flat project structure** (no nested `proj/proj`)
- **Granular modularity** (modules and boxes, not Django "apps")
- **Zero boilerplate** (auto-discovery, no manual registration)

...then Shopyo gives you Django's batteries without Django's constraints.

## Why not plain Flask?

Flask is perfect for small projects. As you grow, you need:
- A **project architecture** that doesn't collapse at 10k lines
- **Auth** that works out of the box (not 6 extensions you wire up yourself)
- An **admin panel** that isn't an afterthought
- **CLI commands** for scaffolding, not copy-paste from Stack Overflow

Shopyo gives you all of this while keeping 100% Flask compatibility. Every Shopyo project is still a Flask project.

## First time contributing?

We have a **100% first-timers friendly policy**. Check out the [testimonials](https://github.com/shopyo/shopyo/discussions/307).

> *"One of the best onboarding experiences I've had. Learned a lot too."* — Ramon from Codesee.io

👉 [Get started contributing](https://shopyo.readthedocs.io/en/latest/contrib.html)
👉 [Join the Discord](https://discord.gg/k37Ef6w)

## License

MIT — see [LICENSE](LICENSE).

## Contact

- [Abdur-Rahmaan Janhangeer](https://github.com/Abdur-rahmaanJ) — arj.python@gmail.com
- [Nathan](https://github.com/blips5)
- [Arthur Nangai](https://github.com/arthurarty) — arthurnangaiarty@yahoo.co.uk
- [Shamsuddin Rehmani](https://github.com/rehmanis) — rehmani@usc.edu
