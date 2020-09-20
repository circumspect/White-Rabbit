# Built-in
from pathlib import Path

# White-Rabbit/src/filepaths.py
WHITE_RABBIT_DIR = Path(__file__).parent.parent

IMAGE_DIR = WHITE_RABBIT_DIR / "Images"
RESOURCE_DIR = IMAGE_DIR / "Player Resources"

CARD_DIR = IMAGE_DIR / "Cards"
CHARACTER_IMAGE_DIR = CARD_DIR / "Characters"
MOTIVE_DIR = CARD_DIR / "Motives"
SUSPECT_IMAGE_DIR = CARD_DIR / "Suspects"
LOCATION_IMAGE_DIR = CARD_DIR / "Locations"
CLUE_DIR = CARD_DIR / "Clues"
