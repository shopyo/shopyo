import datetime
import os
import subprocess
import sys

import pytest

from shopyo.api.info import printinfo


def test_no_args(capfd):
    printinfo()
    year = datetime.datetime.now().year
    captured = capfd.readouterr()
    assert (
        r"""
  / ____| |
 | (___ | |__   ___  _ __  _   _  ___
  \___ \| '_ \ / _ \| '_ \| | | |/ _ \
  ____) | | | | (_) | |_) | |_| | (_) |
 |_____/|_| |_|\___/| .__/ \__, |\___/
                    | |     __/ |
                    |_|    |___/
Copyright {year}""".format(
            year=datetime.datetime.now().year
        )
        in captured.out
    )
