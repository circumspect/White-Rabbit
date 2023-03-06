# Built-in
from os import environ
# 3rd-party
from dotenv import dotenv_values
from rabbit import WHITE_RABBIT_DIR

ENV_FILE = WHITE_RABBIT_DIR / ".env"

DEFAULTS = {
    "WHITE_RABBIT_TOKEN": "0",
    "WHITE_RABBIT_LANGUAGE": "en",
    "WHITE_RABBIT_USE_LOCAL_IMAGES": False,
    "WHITE_RABBIT_PLAYSET": "base"
}


def get_env_var(key: str):
    try:
        var = environ.get(key) or dotenv_values(ENV_FILE)[key]
        var = var.strip()
        if var.lower() == "false":
            return False

        return var
    except KeyError:
        return DEFAULTS[key]
