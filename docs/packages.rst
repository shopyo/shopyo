Packages
========

.. toctree::
   :titlesonly:


Example
-------


.. code:: bash

   # __init__.py


   from typing import Any
   import os
   import json

   from flask import Flask
   from .view import module_blueprint
   from .upload import upload

   __version__ = "1.2.0"

   info = {}
   with open(os.path.dirname(os.path.abspath(__file__)) + os.sep + "info.json") as f:
       info = json.load(f)


   default_config = {"SHOPYO_AUTH_URL": "/shopyo-auth"}


   class ShopyoAuth:
       def __init__(self, app: Any = None) -> None:
           if app is not None:
               self.init_app(app)
           self.upload = upload

       def init_app(self, app: Flask) -> None:
           if not hasattr(app, "extensions"):
               app.extensions = {}

           for key, value in default_config.items():
               app.config.setdefault(key, value)

           app.extensions["shopyo_auth"] = self
           bp = module_blueprint
           app.register_blueprint(bp, url_prefix=app.config["SHOPYO_AUTH_URL"])
           app.jinja_env.globals["shopyo_auth"] = self

       def get_info(self):
           return info


   # pyproject.toml

   [project]
   name = "shopyo_auth"
   authors = [{ name = "Abdur-Rahmaan Janhangeer", email = "arj.python@gmail.com" }]
   description = "Base module containing jinja macros and templates"
   # readme = "README.md"
   requires-python = ">=3.8"
   # license = { file = "LICENSE.txt" }
   keywords = ["shopyo"]
   classifiers = [
       "Programming Language :: Python :: 3",
       "License :: OSI Approved :: BSD License",
       "Operating System :: OS Independent",
   ]
   dependencies = ["shopyo"]
   dynamic = ["version"]

   [tool.setuptools.dynamic]
   version = { attr = "shopyo_auth.__version__" }

   [project.urls]
   "Homepage" = "https://github.com/shopyo/shopyo"
   "Bug Tracker" = "https://github.com/shopyo/shopyo/issues"

   [build-system]
   requires = ["setuptools>=61.0"]
   build-backend = "setuptools.build_meta"

   [tool.setuptools]
   include-package-data = true

   [tool.setuptools.packages.find]
   where = ["."]
   exclude = ["tests*", "docs*", "examples*"]

   [tool.setuptools.package-data]
   shopyo_auth = ["static/**", "templates/**", "*.json"]


   # structure

   shopyo_auth/
      shopyo_auth/
         static/
         templates/
         __init__.py
         decorators.py
         forms.py
         info.json
         models.py
         upload.py
         view.py
      pyproject.toml


   # usage

   from shopyo_auth import ShopyoAuth
   sh_auth = ShopyoAuth()
   sh_auth.init_app(app)
