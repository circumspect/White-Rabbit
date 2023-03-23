# Built-in
import json
import itertools as it
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

pm_channel_format_separator = LOCALIZATION_DATA["channels"]["pm-channel-format"].split("{}")[1]
pm_channel_format_suffix = LOCALIZATION_DATA["channels"]["pm-channel-format"].split("{}")[2]
for nb_characters in range(2, len(characters)):
    for c_sublist in it.combinations(characters, nb_characters):
        LOCALIZATION_DATA["channels"]["texts"]["-".join(c_sublist)] = pm_channel_format_separator.join(c_sublist) + pm_channel_format_suffix

print("Done!")
