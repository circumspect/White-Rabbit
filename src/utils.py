# Built-in
import asyncio
import math
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
TOKEN_FILE = WHITE_RABBIT_DIR / "token.txt"
RESOURCE_DIR = WHITE_RABBIT_DIR / "resources"

IMAGE_DIR = RESOURCE_DIR / "Images"
PLAYER_RESOURCE_DIR = IMAGE_DIR / "Player Resources"
POSTER_DIR = IMAGE_DIR / "Missing Person Posters"
TIMER_AUDIO = WHITE_RABBIT_DIR / "Alice is Missing Playlist.mp3"

CARD_DIR = IMAGE_DIR / "Cards"
CHARACTER_IMAGE_DIR = CARD_DIR / "Characters"
MOTIVE_DIR = CARD_DIR / "Motives"
SUSPECT_IMAGE_DIR = CARD_DIR / "Suspects"
LOCATION_IMAGE_DIR = CARD_DIR / "Locations"
CLUE_DIR = CARD_DIR / "Clues"
SEARCHING_DIR = CARD_DIR / "Searching"

EXPORT_DIR = WHITE_RABBIT_DIR / "exports"
PDF_EXPORT_DIR = EXPORT_DIR / "PDFs"
TEXT_EXPORT_DIR = EXPORT_DIR / "Text"
if not os.path.isdir(EXPORT_DIR):
    os.mkdir(EXPORT_DIR)
if not os.path.isdir(PDF_EXPORT_DIR):
    os.mkdir(PDF_EXPORT_DIR)
if not os.path.isdir(TEXT_EXPORT_DIR):
    os.mkdir(TEXT_EXPORT_DIR)


# Easy access filepaths
MASTER_PATHS = {
    "guide": (PLAYER_RESOURCE_DIR / "Alice is Missing - Guide.jpg"),
    "character_sheet": (PLAYER_RESOURCE_DIR / "Alice is Missing - Character Sheet.jpg"),
    "intro": (CARD_DIR / "Misc" / "Introduction.png"),
}

IMAGE_EXT = ".png"
for character in gamedata.CHARACTERS:
    MASTER_PATHS[character] = (CHARACTER_IMAGE_DIR / gamedata.CHARACTERS[character]).with_suffix(IMAGE_EXT)
for suspect in gamedata.SUSPECTS:
    MASTER_PATHS[suspect] = (SUSPECT_IMAGE_DIR / gamedata.SUSPECTS[suspect]).with_suffix(IMAGE_EXT)
for location in gamedata.LOCATIONS:
    MASTER_PATHS[location] = (LOCATION_IMAGE_DIR / gamedata.LOCATIONS[location]).with_suffix(IMAGE_EXT)

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
            raise ValueError("Cannot send to channel without ctx.text_channels")
        channel = ctx.text_channels[channel]
    asyncio.create_task(channel.send(file=discord.File(filepath)))


def send_folder(channel, path, ctx=None):
    """Sends all images in a folder in alphabetical order"""

    for image in sorted(path.glob("*")):
        send_image(channel, image, ctx)

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
    if not message.replace(' ','').isalnum():
        return False
    
    # If it passes all the above checks it is probably a command attempt
    return True

def remove_emojis(text: str):
    emojis = re.compile(pattern = "["
        u"\U0001F170-\U0001F19A"  # more emojis
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F90C-\U0001F9FF"  # more emojis
                           "]+", flags = re.UNICODE)
    return emojis.sub(r'',text)