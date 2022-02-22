# Built-in
import os

# Local
from utils.localization import DEFAULT_LOCALIZATION, LANGUAGE_KEY
from utils.rabbit import WHITE_RABBIT_DIR

# Temp files
TEMP_DIR = WHITE_RABBIT_DIR / "temp"

# Image paths
# White-Rabbit/src/constants.py
RESOURCE_DIR = WHITE_RABBIT_DIR / "resources"
FONT_DIR = RESOURCE_DIR / "fonts"

IMAGE_DIR = RESOURCE_DIR / "images"
DEFAULT_LOCALIZED_IMAGES_DIR = IMAGE_DIR / DEFAULT_LOCALIZATION
LOCALIZED_IMAGES_DIR = IMAGE_DIR / LANGUAGE_KEY
PLAYER_RESOURCE_DIR = LOCALIZED_IMAGES_DIR / "player-resources"
POSTER_DIR = LOCALIZED_IMAGES_DIR / "posters"

CARD_DIR = LOCALIZED_IMAGES_DIR / "cards"
CHARACTER_IMAGE_DIR = CARD_DIR / "characters"
CHARACTER_INTRODUCTIONS_DIR = CARD_DIR / "introductions"
MOTIVE_DIR = CARD_DIR / "motives"
SUSPECT_IMAGE_DIR = CARD_DIR / "suspects"
LOCATION_IMAGE_DIR = CARD_DIR / "locations"
CLUE_DIR = CARD_DIR / "clues"
SEARCHING_DIR = CARD_DIR / "searching"

EXPORT_DIR = WHITE_RABBIT_DIR / "exports"
PDF_EXPORT_DIR = EXPORT_DIR / "pdfs"
TEXT_EXPORT_DIR = EXPORT_DIR / "text"

# Make export folders if they don't exist
if not os.path.isdir(EXPORT_DIR):
    os.mkdir(EXPORT_DIR)
if not os.path.isdir(PDF_EXPORT_DIR):
    os.mkdir(PDF_EXPORT_DIR)
if not os.path.isdir(TEXT_EXPORT_DIR):
    os.mkdir(TEXT_EXPORT_DIR)
if not os.path.isdir(TEMP_DIR):
    os.mkdir(TEMP_DIR)
