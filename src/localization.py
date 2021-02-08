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


with open(LOCALIZATIONS["en"]) as f:
    localization = json.loads(f.read())
