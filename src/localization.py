# Built-in
import json
from pathlib import Path
# 3rd-party
from dotenv import dotenv_values

# White-Rabbit/src/localization.py
WHITE_RABBIT_DIR = Path(__file__).parent.parent

# Localization
LOCALIZATION_DIR = WHITE_RABBIT_DIR / "localization"

LOCALIZATIONS = {
    "en": "english.json",
    "fr": "french.json",
}

config = dotenv_values(".env")
localization_file = LOCALIZATION_DIR / LOCALIZATIONS[config["LANGUAGE"]]

LOCALIZATION_DATA = None
with open(localization_file) as f:
    LOCALIZATION_DATA = json.loads(f.read())
