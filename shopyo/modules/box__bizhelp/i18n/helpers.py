langs = {"en": "english", "fr": "french"}


def lang_keys():
    return (k for k in langs)


def get_current_language():
    return session["yo_current_language"]
