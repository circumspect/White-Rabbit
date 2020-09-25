# Built-in
import asyncio
import os
from pathlib import Path
import re
# 3rd-party
import discord
# Local
import gamedata

# Image paths
# White-Rabbit/src/utils.py
WHITE_RABBIT_DIR = Path(__file__).parent.parent

IMAGE_DIR = WHITE_RABBIT_DIR / "Images"
RESOURCE_DIR = IMAGE_DIR / "Player Resources"
POSTER_DIR = IMAGE_DIR / "Missing Person Posters"
TIMER_AUDIO = WHITE_RABBIT_DIR / "Alice is Missing Playlist.mp3"

CARD_DIR = IMAGE_DIR / "Cards"
CHARACTER_IMAGE_DIR = CARD_DIR / "Characters"
MOTIVE_DIR = CARD_DIR / "Motives"
SUSPECT_IMAGE_DIR = CARD_DIR / "Suspects"
LOCATION_IMAGE_DIR = CARD_DIR / "Locations"
CLUE_DIR = CARD_DIR / "Clues"
SEARCHING_DIR = CARD_DIR / "Searching"

EXPORT_DIR = WHITE_RABBIT_DIR / "Exports"
PDF_EXPORT_DIR = EXPORT_DIR / "PDFs"
if not os.path.isdir(EXPORT_DIR):
    os.mkdir(EXPORT_DIR)
if not os.path.isdir(PDF_EXPORT_DIR):
    os.mkdir(PDF_EXPORT_DIR)


# Easy access filepaths
MASTER_PATHS = {
    "guide": (RESOURCE_DIR / "Alice is Missing - Guide.jpg"),
    "character_sheet": (RESOURCE_DIR / "Alice is Missing - Character Sheet.jpg"),
    "intro": (CARD_DIR / "Misc" / "Introduction.png"),
}

IMAGE_EXT = ".png"
for character in gamedata.CHARACTERS:
    MASTER_PATHS[character] = (CHARACTER_IMAGE_DIR / gamedata.CHARACTERS[character]).with_suffix(IMAGE_EXT)
for suspect in gamedata.SUSPECTS:
    MASTER_PATHS[suspect] = (SUSPECT_IMAGE_DIR / gamedata.SUSPECTS[suspect]).with_suffix(IMAGE_EXT)
for location in gamedata.LOCATIONS:
    MASTER_PATHS[location] = (LOCATION_IMAGE_DIR / gamedata.LOCATIONS[location]).with_suffix(IMAGE_EXT)


def get_text_channels(guild):
    return {
        channel.name: channel
        for channel in guild.text_channels
    }


def send_image(channel, filepath, ctx=None):
    """Sends an image to a specified channel"""

    if isinstance(channel, str):
        if not ctx:
            raise ValueError("Cannot send to channel without ctx.text_channels")
        channel = ctx.text_channels[channel]
    asyncio.create_task(channel.send(file=discord.File(filepath)))


def send_folder(channel, path, ctx=None):
    """Sends all images in a folder in alphabetical order"""

    for image in sorted(path.glob("*")):
        send_image(channel, image, ctx)

def remove_emojis(text: str):
    emojis = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return emojis.sub(r'',text)