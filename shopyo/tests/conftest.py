import os
import shutil

import pytest

from shopyo.api.file import tryrmtree
from shopyo.app import app as _app
from shopyo.app import create_app


@pytest.fixture
def app(tmpdir, app_type):
    src = os.path.join(_app.instance_path, "config.py")
    dest = tmpdir.join("temp_config.py")
    dest.write("")
    shutil.copy(src, dest)
    tryrmtree(_app.instance_path)
    dev_app = create_app(app_type)
    yield dev_app
    shutil.copy(dest, src)
