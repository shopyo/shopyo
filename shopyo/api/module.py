import copy
import json
import os

from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for

from shopyo.api.assets import get_static


class ModuleHelp:
    def __init__(self, dunderfile, dundername):
        self.dirpath = os.path.dirname(os.path.abspath(dunderfile))
        self.template_folder = os.path.join(self.dirpath, "templates")
        self.info = {}
        self._context = {}

        with open(self.dirpath + "/info.json") as f:
            self.info = json.load(f)

        self.blueprint_str = "{}_blueprint".format(self.info["module_name"])
        self.blueprint = Blueprint(
            "{}".format(self.info["module_name"]),
            dundername,
            template_folder=self.template_folder,
            url_prefix=self.info["url_prefix"],
        )

        self._context.update({"info": self.info})

    def render(self, filename, **kwargs):
        """
        renders file.html found in module/templates/module/file.html
        """
        return render_template(
            "{}/{}".format(self.info["module_name"], filename), **kwargs
        )

    def redirect_url(self, url, **kwargs):
        return redirect(url_for(url, **kwargs))

    def context(self):
        return copy.deepcopy(self._context)

    def method(self, methodname):
        return "{}.{}".format(self.info["module_name"], methodname)

    def get_self_static(self, filename):
        module_parent = os.path.dirname(self.dirpath)
        module_folder = self.dirpath

        module_parent = os.path.normpath(module_parent)
        module_parent = os.path.basename(module_parent)

        module_folder = os.path.normpath(module_folder)
        module_folder = os.path.basename(module_folder)

        if module_parent.startswith("box__"):
            boxormodule = f"{module_parent}/{module_folder}"
        else:
            boxormodule = module_folder
        return get_static(boxormodule=boxormodule, filename=filename)


def iter_modules(project_root):
    """
    Yields (module_name, module_path) for every valid module in the project,
    transparently handling both standalone modules and ``'box__'`` nested modules.

    Yields:
        module_name (str): Dot-separated python path (e.g., 'modules.box__shop.cart')
        module_path (str): Absolute file system path to the module directory.
    """
    modules_dir = os.path.join(project_root, "modules")
    if not os.path.exists(modules_dir):
        return

    for folder in os.listdir(modules_dir):
        if folder.startswith("__"):
            continue

        abs_folder_path = os.path.join(modules_dir, folder)

        if folder.startswith("box__"):
            # It's a box, iterate its children
            for sub in os.listdir(abs_folder_path):
                if sub.startswith("__") or sub.endswith(".json"):
                    continue

                # Yield box module
                yield f"modules.{folder}.{sub}", os.path.join(abs_folder_path, sub)
        else:
            # It's a standard module
            yield f"modules.{folder}", abs_folder_path
