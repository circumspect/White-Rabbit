# Built-in
import json
import logging
# Local
from data import cards
import envvars

# White-Rabbit/src/localization.py
from rabbit import WHITE_RABBIT_DIR

# Localization
DEFAULT_LOCALIZATION = envvars.DEFAULTS["WHITE_RABBIT_LANGUAGE"]
LOCALIZATION_DIR = WHITE_RABBIT_DIR / "localization"

LANGUAGE_KEY = envvars.get_env_var("WHITE_RABBIT_LANGUAGE")

localization_file = LOCALIZATION_DIR / f"{LANGUAGE_KEY}.json"

logging.info(f"Loading localization data ({LANGUAGE_KEY})... ")

LOCALIZATION_DATA = None
with open(localization_file, encoding='utf-8') as f:
    LOCALIZATION_DATA = json.load(f)

LOCALIZATION_DATA["channels"]["clues"] = {}
characters = [name for name in cards.CHARACTERS]
for character in characters:
    channel = LOCALIZATION_DATA["channels"]["clue-channel-format"].format(character)
    LOCALIZATION_DATA["channels"]["clues"][character] = channel

LOCALIZATION_DATA["channels"]["texts"] = {}
LOCALIZATION_DATA["channels"]["texts"]["group-chat"] = LOCALIZATION_DATA["channels"]["group-chat"]

for i, char1 in enumerate(characters):
    # Create list of character pairs
    for j in range(i+1, len(characters)):
        char2 = characters[j]
        channel = LOCALIZATION_DATA["channels"]["pm-channel-format"].format(char1, char2)
        LOCALIZATION_DATA["channels"]["texts"][f"{char1}-{char2}"] = channel

logging.info("Localization data loaded!")
