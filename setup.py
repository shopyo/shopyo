"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject


python setup.py publish to publish

"""
from setuptools import setup
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))

if sys.argv[-1] == "publish":  # requests
    os.system("python setup.py sdist")  # bdist_wheel
    os.system("twine upload dist/* --skip-existing")
    sys.exit()

setup(
    install_requires=open(
        os.path.join(here, "requirements.txt"), encoding="utf-8"
    )
    .read()
    .split("\n")
)
