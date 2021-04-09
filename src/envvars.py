# Built-in
from os import environ
# 3rd-party
from dotenv import dotenv_values
from rabbit import WHITE_RABBIT_DIR

ENV_FILE = WHITE_RABBIT_DIR / ".env"

DEFAULTS = {
    "TOKEN": "0",
    "LANGUAGE": "en",
    "USE_LOCAL_IMAGES": False,
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
