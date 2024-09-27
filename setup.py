"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject


python setup.py publish to publish

"""

import os
import sys

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

if sys.argv[-1] == "publish":  # requests
    os.system("python setup.py sdist")  # bdist_wheel
    os.system("twine upload dist/* --skip-existing")
    sys.exit()

setup(
    install_requires=open(
        os.path.join(here, "requirements/requirements.txt"), encoding="utf-8"
    )
    .read()
    .split("\n"),
    url="https://github.com/shopyo/shopyo",
)
