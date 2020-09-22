# Built-in
from pathlib import Path
# Local
import gamedata

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

# Easy access filepaths
MASTER_PATHS = {
    "guide": (RESOURCE_DIR / "Alice is Missing - Guide.jpg"),
    "character_sheet": (RESOURCE_DIR / "Alice is Missing - Character Sheet.jpg"),
    "intro": (CARD_DIR / "Misc" / "Introduction.png"),
    }

IMAGE_EXT = ".png"
for character in (gamedata.CHARACTERS):
    MASTER_PATHS[character] = CHARACTER_IMAGE_DIR / (gamedata.CHARACTERS[character] + IMAGE_EXT)
for suspect in (gamedata.SUSPECTS):
    MASTER_PATHS[suspect] = SUSPECT_IMAGE_DIR / (gamedata.SUSPECTS[suspect] + IMAGE_EXT)
for location in (gamedata.LOCATIONS):
    MASTER_PATHS[location] = LOCATION_IMAGE_DIR / (gamedata.LOCATIONS[location] + IMAGE_EXT)


def get_text_channels(guild):
    return {
        channel.name: channel
        for channel in guild.text_channels
    }