import os
import shutil

import pytest
from app import app as _app
from app import create_app

from shopyo.api.file import tryrmtree


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
