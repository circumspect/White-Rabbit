# Built-in
import json
# 3rd-party
from dotenv import dotenv_values
# Local
import utils

LOCALIZATION_DIR = utils.WHITE_RABBIT_DIR / "localization"

LOCALIZATIONS = {
    "en": LOCALIZATION_DIR / "english.json"
}

config = dotenv_values(".env")
localization_file = LOCALIZATIONS[config["LANGUAGE"]]

LOCALIZATION_DATA = None
with open(localization_file) as f:
    LOCALIZATION_DATA = json.loads(f.read())
