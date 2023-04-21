import logging

import discord


LOGGING_FORMATTER = discord.utils._ColourFormatter()
LOGGING_HANDLER = logging.StreamHandler()
LOGGING_HANDLER.setFormatter(LOGGING_FORMATTER)


def get_logger(name: str):
    if name == "__main__":
        logger = logging.getLogger(f"white-rabbit")
        logger.setLevel(logging.INFO)
        logger.addHandler(LOGGING_HANDLER)
    else:
        logger = logging.getLogger(f"white-rabbit.{name}")

    return logger
