# Built-in
from os import environ
# 3rd-party
from dotenv import dotenv_values


def get_env_var(key: str):
    var = environ.get(key) or dotenv_values(".env")[key]
    if var.lower() == "false":
        return False

    return var
