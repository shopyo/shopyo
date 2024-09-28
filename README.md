<h1 align="center">
  <br>
  <a href="https://github.com/shopyo"><img src="https://github.com/shopyo/shopyo/blob/dev/assets/github_banner.png" alt="shopyo" width="" height=""></a>

</h1>

[![Downloads](https://static.pepy.tech/badge/shopyo/month)](https://pepy.tech/project/shopyo) [![Codecov](https://codecov.io/gh/shopyo/shopyo/branch/dev/graph/badge.svg?token=J4TL2MDTSS)](https://codecov.io/gh/shopyo/shopyo) ![Tests](https://github.com/shopyo/shopyo/actions/workflows/tests.yaml/badge.svg) [![PyPI version shields.io](https://img.shields.io/pypi/v/shopyo.svg)](https://pypi.python.org/pypi/shopyo/) [![Documentation Status](https://readthedocs.org/projects/shopyo/badge/?version=latest)](https://shopyo.readthedocs.io/en/latest/?badge=latest) [![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/5350/badge)](https://bestpractices.coreinfrastructure.org/projects/5350) [![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/shopyo/shopyo/badge)](https://api.securityscorecards.dev/projects/github.com/shopyo/shopyo)

Featured on [Weekly Python issue 436](https://newsletry.com/Home/Python%20Weekly/9a578693-14ba-47c5-8a8e-08d7b0139fe7) 🌟

A 45 mins talk was dedicated to it at [EuroPython](https://youtu.be/rkzXQOC1T0Q) 🌟

Must watch: [Shopyo: Your Mega Flask Machine](https://youtu.be/pvwvRi6iMds) (short vid)

E-commerce modules transferred to [ShopCube](https://github.com/shopyo/shopcube)

**[ [DOCS](https://shopyo.readthedocs.io/en/latest/) | [DISCORD](https://discord.gg/k37Ef6w) | [CONTRIBUTE](https://shopyo.readthedocs.io/en/latest/contrib.html) | [TWITTER](https://twitter.com/shopyoproject)]**

# What?

Your next-level modular web framework. Get organisation & scalability from day 1.

Built on top of Flask, it offers most Django features, sometimes a tidbit more with far more flexibility.

# Why?

| Perk |  |
|:--|:--:|
| 🥏 No learning  | Does not get into the way, uses common flask-packages. You only need to know Flask. |
| 🏗️ Architecture | Never think about architecture of your app, just build & integrate extensions. |
| 🏢 Scalable | As your app grows, Shopyo caters for your codebase with powerful features. |
| 🥢 Good practices | Testing, docs etc are covered. Don't make those afterthoughts. |
| 🔧 Ease your life | We've been there. Awesome utils to ease development. |
| 🪜 Scaffolding | Don't waste time writing boilerplate code. We've got you covered. |
| 🖍️ Theming system | You need theme in your apps? We integrate a default theme system. |

# Features

- ⚛️ i18n setup
- 🔐 Login & Auth
- 📧 Email
- 📦 2-level modularity
- 🪐 Designed for really BIG apps
- 🌅 Assets management

# Quick start

```bash
pip install shopyo # always ensure latest version
mkdir blog
cd blog
shopyo new -m # add default modules
cd blog
shopyo initialise
python
>>> from app import create_app()
>>> from shopyo_auth.upload import add_admin
>>> from init import db
>>> a = create_app()
>>> with a.create_app():
>>> add_admin('admin@domain.com', 'pass')
>>>     db.session.commit()
flask run --debug
```


```bash
pip install shopyo>=4.11
mkdir blog
cd blog
shopyo new
cd blog
flask run --debug
```

If errors do (linux, use `set <VAR>` for Windows):

```
export SHOPYO_CONFIG_PROFILE=development
export FLASK_ENV=development # < flask 2.2.x
export ENV=development
export FLASK_DEBUG=development # < flask 2.2.x
export FLASK_APP=app.py
```

`SHOPYO_CONFIG_PROFILE` is what is defined as keys of `app_config` in `config.py`

It is recommended to use a venv in root folder.

`python -m venv venv`

If for dev install dev_requirements.txt also.

`python -m pip install -r requirements/dev.txt`

go to http://127.0.0.1:5000/dashboard with credentials admin@domain.com / pass

![](https://github.com/shopyo/shopyo/blob/dev/comparison.png)

-   Not framework docs but docs for the project you are building.

# First time contributing?

We have a 100% first-timers friendly policy. Check out the [testimonials](https://github.com/shopyo/shopyo/discussions/307).

> Thank you! One of the best onboarding experiences I've had. Learned a lot too (Ramon from Codesee.io)

# Glimpse

![](https://github.com/shopyo/shopyo/raw/dev/assets/comparison.png)

# Who uses Shopyo?

|   site name    |    description     |
| :------------: | :----------------: |
| Maurilearn.com | Elearning platform |
| Linkolearn.com |   Learn By links   |
|  FlaskCon.com  |  Conference soft   |

# Big??

Powered by apps / modules. Add as many as you like.

Apps are not enough, organise them in boxes and get the ultimate order you need.

You need a customised Django? This is the project. You need to build an ERP? This is the project.

# Linux??

Hackable to the core. Even the dashboard is but a module.

Don't need our modules? Nuke them. Look boring? modify them

# Reliable?

We don't maintain middlewares. We rely on battle tested batteries like:

-   flask_sqlalchemy
-   flask_login & co

Heck remove them if you don't want. Want to use Peewee? You can.

# Rich Flask API

Common flask patterns are integrated, the structure is over the moon.

Common flask tasks are provided with an API: custom notifications, bulk form errors

# Back office feel & Theme

All looks are 100% customisable with themes ~ Backend, bootstrap included by default.

Again blow it up & use what you want. It's possible

# Transparent: Code your own web distro

Everything is clear, not hidden. You can 100% customise whatever you want.

We did not hardcode our choices. Our APIS are incremental. You can always use barebones.

# Plug & Play

The modules are put by copy paste. No blueprint codes to write.

# Contribute

We follow a 100% first-timers friendly policy.

👉 Get started [here](https://shopyo.readthedocs.io/en/latest/contrib.html)

👉 Join the [Discord](https://discord.gg/k37Ef6w), ask questions & learn about Flask tricks during our dev talks!

# 📚 Docs

👉 Link: [shopyo.readthedocs.io/](https://shopyo.readthedocs.io/en/latest/)

# 📞 Contact (inlcuding in case of vulns)

Support team if you are stuck

-   [Abdur-Rahmaan Janhangeer](https://github.com/Abdur-rahmaanJ) - arj.python@gmail.com
-   [Nathan](https://github.com/blips5) -
-   [Arthur Nangai](https://github.com/arthurarty) - arthurnangaiarty@yahoo.co.uk
-   [Shamsuddin Rehmani](https://github.com/rehmanis) - rehmani@usc.edu
