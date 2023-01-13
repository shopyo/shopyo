import os


def is_yo_debug():
    debug_val = os.environ.get("SHOPYO_DEBUG", "0")

    if debug_val.casefold() in ["1", "true", "yes"]:
        return True
    else:
        return False
