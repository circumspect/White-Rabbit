# Built-in
import asyncio
import math
import random
import os
from pathlib import Path
import re
# 3rd-party
import discord
# Local
import gamedata
from localization import DEFAULT_LOCALIZATION, LOCALIZATION_DATA, language_key
from resources import ImageResource

# Links
DOCS_URL = "https://white-rabbit.readthedocs.io/"
DOCS_SHORT_URL = "https://white-rabbit.rtfd.io/"
SOURCE_URL = "https://github.com/circumspect/White-Rabbit"
BLANK_DOTENV_URL = "https://raw.githubusercontent.com/circumspect/White-Rabbit/main/example.env"

# Console logging message stuff
LOG_SEP = ": "
INFO_PREFIX = "INFO" + LOG_SEP
WARNING_PREFIX = "WARNING" + LOG_SEP
ERROR_PREFIX = "ERROR" + LOG_SEP

# Image paths
# White-Rabbit/src/utils.py
WHITE_RABBIT_DIR = Path(__file__).parent.parent
ENV_FILE = WHITE_RABBIT_DIR / ".env"
DEV_ID_FILE = WHITE_RABBIT_DIR / "dev_ids.txt"
RESOURCE_DIR = WHITE_RABBIT_DIR / "resources"

IMAGE_DIR = RESOURCE_DIR / "Images"
DEFAULT_LOCALIZED_IMAGES_DIR = IMAGE_DIR / DEFAULT_LOCALIZATION
LOCALIZED_IMAGES_DIR = IMAGE_DIR / language_key
PLAYER_RESOURCE_DIR = LOCALIZED_IMAGES_DIR / "Player Resources"
POSTER_DIR = LOCALIZED_IMAGES_DIR / "Missing Person Posters"
TIMER_AUDIO = WHITE_RABBIT_DIR / "Alice is Missing Playlist.mp3"

CARD_DIR = LOCALIZED_IMAGES_DIR / "Cards"
CHARACTER_IMAGE_DIR = CARD_DIR / "Characters"
MOTIVE_DIR = CARD_DIR / "Motives"
SUSPECT_IMAGE_DIR = CARD_DIR / "Suspects"
LOCATION_IMAGE_DIR = CARD_DIR / "Locations"
CLUE_DIR = CARD_DIR / "Clues"
SEARCHING_DIR = CARD_DIR / "Searching"

EXPORT_DIR = WHITE_RABBIT_DIR / "exports"
PDF_EXPORT_DIR = EXPORT_DIR / "PDFs"
TEXT_EXPORT_DIR = EXPORT_DIR / "Text"

# Make export folders if they don't exist
if not os.path.isdir(EXPORT_DIR):
    os.mkdir(EXPORT_DIR)
if not os.path.isdir(PDF_EXPORT_DIR):
    os.mkdir(PDF_EXPORT_DIR)
if not os.path.isdir(TEXT_EXPORT_DIR):
    os.mkdir(TEXT_EXPORT_DIR)

def get_image(directory: Path, name: str) -> Path:
    img = ImageResource(ImageResource.ALLOWED_EXTENSIONS)
    try:
        return img.get(directory, name)
    except FileNotFoundError:
        parts = list(directory.parts)
        for i in range(len(parts)):
            if parts[i] == "White-Rabbit":
                if parts[i+3] != "shared":
                    parts[i+3] = DEFAULT_LOCALIZATION
                    break

        return img.get(Path("/".join(parts)), name)


# Easy access filepaths
MASTER_PATHS = {
    "guide": get_image(PLAYER_RESOURCE_DIR, "Alice is Missing - Guide"),
    "character_sheet": get_image(PLAYER_RESOURCE_DIR, "Alice is Missing - Character Sheet"),
    "intro": get_image(CARD_DIR / "Misc", "Introduction"),
    "debrief": get_image(CARD_DIR / "Misc", "Debrief"),
}


for character in gamedata.CHARACTERS:
    MASTER_PATHS[character] = get_image(CHARACTER_IMAGE_DIR, gamedata.CHARACTERS[character])
for suspect in gamedata.SUSPECTS:
    MASTER_PATHS[suspect] = get_image(SUSPECT_IMAGE_DIR, gamedata.SUSPECTS[suspect])
for location in gamedata.LOCATIONS:
    MASTER_PATHS[location] = get_image(LOCATION_IMAGE_DIR, gamedata.LOCATIONS[location])


def flip():
    return random.choice([LOCALIZATION_DATA["flip"]["heads"], LOCALIZATION_DATA["flip"]["tails"]])


def codeblock(text: str):
    return f"```{text}```"


def get_text_channels(guild):
    return {
        channel.name: channel
        for channel in guild.text_channels
    }


def time_string(time):
    """Takes # of seconds and returns formatted string mm:ss"""

    def pad(num):
        return str(int(num)).zfill(2)

    minutes = pad(math.floor(time / 60))
    seconds = pad(time % 60)

    return f"{minutes}:{seconds}"


def send_image(channel, filepath, ctx=None):
    """Sends an image to a specified channel"""

    if isinstance(channel, str):
        if not ctx:
            raise ValueError(
                "Cannot send to channel without ctx.text_channels"
            )
        channel = ctx.text_channels[channel]

    asyncio.create_task(channel.send(file=discord.File(filepath)))


def send_folder(channel, path, ctx=None):
    """Sends all images in a folder in alphabetical order"""

    for image in sorted(path.glob("*.*")):
        filepath = get_image(path, image.stem)
        send_image(channel, filepath, ctx)


def is_command(message: str):
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


def clean_message(ctx, text: str):
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


def ooc_strip(ctx, text: str):
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
