import os
from pathlib import Path
# Local
import gamedata
from localization import DEFAULT_LOCALIZATION, LANGUAGE_KEY
import utils

# Links and bot info
VERSION = "0.7.0"
DOCS_URL = "https://white-rabbit.readthedocs.io/"
DOCS_SHORT_URL = "https://white-rabbit.rtfd.io/"
SOURCE_URL = "https://github.com/circumspect/White-Rabbit"
BLANK_DOTENV_URL = f"https://raw.githubusercontent.com/circumspect/White-Rabbit/{VERSION}/example.env"

# Console logging message stuff
LOG_SEP = ": "
INFO_PREFIX = "INFO" + LOG_SEP
WARNING_PREFIX = "WARNING" + LOG_SEP
ERROR_PREFIX = "ERROR" + LOG_SEP

# Image paths
# White-Rabbit/src/constants.py
WHITE_RABBIT_DIR = Path(__file__).parent.parent
ENV_FILE = WHITE_RABBIT_DIR / ".env"
DEV_ID_FILE = WHITE_RABBIT_DIR / "dev_ids.txt"
RESOURCE_DIR = WHITE_RABBIT_DIR / "resources"

IMAGE_DIR = RESOURCE_DIR / "images"
DEFAULT_LOCALIZED_IMAGES_DIR = IMAGE_DIR / DEFAULT_LOCALIZATION
LOCALIZED_IMAGES_DIR = IMAGE_DIR / LANGUAGE_KEY
PLAYER_RESOURCE_DIR = LOCALIZED_IMAGES_DIR / "Player-Resources"
POSTER_DIR = LOCALIZED_IMAGES_DIR / "Posters"
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

# Easy access filepaths
MASTER_PATHS = {
    "guide": utils.get_image(PLAYER_RESOURCE_DIR, "Guide"),
    "character_sheet": utils.get_image(PLAYER_RESOURCE_DIR, "Character-Sheet"),
    "intro": utils.get_image(CARD_DIR / "Misc", "Introduction"),
    "debrief": utils.get_image(CARD_DIR / "Misc", "Debrief"),
}

for character in gamedata.CHARACTERS:
    MASTER_PATHS[character] = utils.get_image(CHARACTER_IMAGE_DIR, character)
for suspect in gamedata.SUSPECTS:
    MASTER_PATHS[suspect] = utils.get_image(SUSPECT_IMAGE_DIR, suspect)
for location in gamedata.LOCATIONS:
    MASTER_PATHS[location] = utils.get_image(LOCATION_IMAGE_DIR, location)

# Make export folders if they don't exist
if not os.path.isdir(EXPORT_DIR):
    os.mkdir(EXPORT_DIR)
if not os.path.isdir(PDF_EXPORT_DIR):
    os.mkdir(PDF_EXPORT_DIR)
if not os.path.isdir(TEXT_EXPORT_DIR):
    os.mkdir(TEXT_EXPORT_DIR)
