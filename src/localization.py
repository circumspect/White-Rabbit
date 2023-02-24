# Built-in
import json
# Local
import cards
import envvars

# White-Rabbit/src/localization.py
from rabbit import WHITE_RABBIT_DIR

# Localization
DEFAULT_LOCALIZATION = envvars.DEFAULTS["LANGUAGE"]
LOCALIZATION_DIR = WHITE_RABBIT_DIR / "localization"

LOCALIZATIONS = {
    "en": "english.json",
    "fr": "french.json",
    "de": "german.json",
    "it": "italian.json",
}

LANGUAGE_KEY = envvars.get_env_var("LANGUAGE")

localization_file = LOCALIZATION_DIR / LOCALIZATIONS[LANGUAGE_KEY]

print(f"Loading localization data ({LANGUAGE_KEY})... ", end="")

LOCALIZATION_DATA = None
with open(localization_file, encoding='utf-8') as f:
    LOCALIZATION_DATA = json.load(f)

LOCALIZATION_DATA["channels"]["clues"] = {}
characters = [name for name in cards.CHARACTERS]
for character in characters:
    LOCALIZATION_DATA["channels"]["clues"][character] = LOCALIZATION_DATA["channels"]["clue-channel-format"].format(character)

LOCALIZATION_DATA["channels"]["texts"] = {}
LOCALIZATION_DATA["channels"]["texts"]["group-chat"] = LOCALIZATION_DATA["channels"]["group-chat"]

for i, char1 in enumerate(characters):
    # Create list of character pairs
    for j in range(i+1, len(characters)):
        char2 = characters[j]
        LOCALIZATION_DATA["channels"]["texts"][f"{char1}-{char2}"] = LOCALIZATION_DATA["channels"]["pm-channel-format"].format(char1, char2)

print("Done!")
