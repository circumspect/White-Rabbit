# Built-in
import json
from os import environ
from pathlib import Path
# 3rd-party
from dotenv import dotenv_values
from resources import LocalizedResource

# White-Rabbit/src/localization.py
WHITE_RABBIT_DIR = Path(__file__).parent.parent

# Localization
LOCALIZATION_DIR = WHITE_RABBIT_DIR / "localization"

LOCALIZATIONS = {
    "en": "english.json",
    "fr": "french.json",
}

try:
    language_key = environ.get("LANGUAGE") or dotenv_values(".env")["LANGUAGE"]
except KeyError:
    language_key = "en"

localization_file = LOCALIZATION_DIR / LOCALIZATIONS[language_key]

LOCALIZATION_DATA = None
with open(localization_file) as f:
    LOCALIZATION_DATA = json.loads(f.read())

LOCALIZATION_RESOURCES = LocalizedResource(language_key)
