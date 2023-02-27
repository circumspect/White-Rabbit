# pylint: disable=unsubscriptable-object   # https://github.com/PyCQA/pylint/issues/3637#issuecomment-720097674

# Built-in
import math
import os
from pathlib import Path
import random
import re
import subprocess
from typing import List, Union
# 3rd-party
import discord
from discord.ext import commands
import requests
# Local
from data import constants
from data.localization import DEFAULT_LOCALIZATION, LOCALIZATION_DATA, LANGUAGE_KEY
import envvars
from rabbit import WHITE_RABBIT_DIR
from resources import ImageResource


def flip():
    return random.choice([LOCALIZATION_DATA["flip"]["heads"], LOCALIZATION_DATA["flip"]["tails"]])


def codeblock(text: str):
    return f"```{text}```"


def get_text_channels(guild: discord.Guild):
    return {
        channel.name: channel
        for channel in guild.text_channels
    }


def time_string(time: int):
    """Takes # of seconds and returns formatted string mm:ss"""

    def pad(num):
        return str(int(num)).zfill(2)

    minutes = pad(math.floor(time / 60))
    seconds = pad(time % 60)

    return f"{minutes}:{seconds}"


def delete_files(dir: Path, ext: str):
    for root, _, files in os.walk(dir, topdown=False):
        for name in files:
            if name.split(".")[-1] == ext:
                os.remove(os.path.join(root, name))


def rabbit_path(path: Path):
    parts = list(path.parts)
    start = 1
    for i in range(len(parts)):
        if parts[i] == WHITE_RABBIT_DIR.name:
            start = i + 1

    return Path("/".join(parts[start:]))


def url_is_good(url: str):
    r = requests.get(url)
    return r.status_code == 200


def find_url(url: str, extensions: List[str]):
    for extension in extensions:
        image_url = f"{url}.{extension}"
        if url_is_good(image_url):
            return image_url

    raise FileNotFoundError(url)


def get_image(directory: Path, name: str) -> Union[Path, str]:
    if envvars.get_env_var("WHITE_RABBIT_USE_LOCAL_IMAGES"):
        img = ImageResource(ImageResource.DEFAULT_EXTENSIONS)
        try:
            return img.get(directory, name)
        except FileNotFoundError:
            parts = list(directory.parts)
            for i in range(len(parts)):
                if parts[i] == "White-Rabbit" and parts[i + 3] == LANGUAGE_KEY:
                    parts[i+3] = DEFAULT_LOCALIZATION
                    break

            return img.get(Path("/".join(parts)), name)

    else:
        path = rabbit_path(directory)
        parts = path.parts
        url = constants.RAW_FILES_URL

        localized_url = f"{url}{'/'.join(parts)}/{name}"
        try:
            return find_url(localized_url, ImageResource.DEFAULT_EXTENSIONS)
        except FileNotFoundError:
            if parts[2] == LANGUAGE_KEY:
                fallback = list(parts)
                fallback[2] = DEFAULT_LOCALIZATION

            fallback_url = f"{url}{'/'.join(fallback)}/{name}"
            return find_url(fallback_url, ImageResource.DEFAULT_EXTENSIONS)


async def send_image(channel: discord.TextChannel, filepath: Union[Path, str], ctx: commands.Context=None):
    """Sends an image to a specified channel"""

    if isinstance(channel, str):
        if not ctx:
            raise ValueError(
                "Cannot send to channel without ctx.text_channels"
            )
        channel = ctx.text_channels[channel]

    if isinstance(filepath, Path):
        # If sending image as a file, attach it
        await channel.send(file=discord.File(filepath))
    else:
        # Otherwise send the link directly
        await channel.send(filepath)


async def send_folder(channel, path, ctx: commands.Context=None):
    """Sends all images in a folder in alphabetical order"""

    for image in sorted(path.glob("*.*")):
        filepath = get_image(path, image.stem)
        await send_image(channel, filepath, ctx)


def is_command(message: str):  # sourcery skip: return-identity
    """Checks if a string seems like an attempt to send a command"""

    # Check if message has ! prefix
    if not message.startswith("!"):
        return False
    # If space after the !, not a command
    if message.startswith("! "):
        return False

    # Remove ! from start of string
    message = message[1:]

    # If string contains non-alphanumeric characters (besides spaces)
    # then it is not a command
    if not message.replace(' ', '').isalnum():
        return False

    # If it passes all the above checks it is probably a command attempt
    return True


def clean_message(ctx: commands.Context, text: str):
    """Removes emojis and out of character parts of a string"""

    text = remove_emojis(text).strip()
    text = ooc_strip(ctx, text).strip()

    return text


def remove_emojis(text: str):
    emojis = re.compile(pattern="["
                        u"\U0001F170-\U0001F19A"  # more emojis
                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                        u"\U0001F600-\U0001F64F"  # emoticons
                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                        u"\U0001F90C-\U0001F9FF"  # more emojis
                        "]+", flags=re.UNICODE)

    return emojis.sub(r'', text)


def ooc_strip(ctx: commands.Context, text: str):
    """
    Takes a string and removes out of context portions

    String should be stripped of whitespace first
    """

    # If entire message is out of character, ignore
    if ctx.game.ooc_strip_level >= 1:
        if text.startswith("(") and text.endswith(")"):
            return ""

    # If using aggressive removal for OOC messages, greedy remove anything
    # inside parentheses
    if ctx.game.ooc_strip_level >= 2:
        re.sub(r'\([^)]*\)', '', text)

    return text

def upload_file(path: Path):
    """Uploads a file and returns the download URL"""

    return subprocess.run(["curl", "-T", path, "https://transfer.sh/Alice.pdf"],
                          check=True, capture_output=True, text=True
                          ).stdout.strip()
