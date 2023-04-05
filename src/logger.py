import logging

import discord


LOGGING_FORMATTER = discord.utils._ColourFormatter()
LOGGING_HANDLER = logging.StreamHandler()
LOGGING_HANDLER.setLevel(logging.INFO)
LOGGING_HANDLER.setFormatter(LOGGING_FORMATTER)


def get_logger(name: str):
    logger = logging.getLogger(f"white-rabbit.{name}")
    logger.setLevel(logging.INFO)
    logger.addHandler(LOGGING_HANDLER)

    return logger
