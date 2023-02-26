# Built-in
import envvars
import random
import yaml
# Local
from rabbit import WHITE_RABBIT_DIR


CARD_LIST_DIR = WHITE_RABBIT_DIR / "card_lists"

with open(CARD_LIST_DIR / f"{envvars.get_env_var('WHITE_RABBIT_CARD_LIST')}.yaml", "r") as f:
    CARD_LIST = yaml.safe_load(f)

CHARACTERS = CARD_LIST["characters"]
for character in CHARACTERS:
    if CHARACTERS[character] is None:
        CHARACTERS[character] = {}

    if "role" not in CHARACTERS[character] or CHARACTERS[character]["role"] is None:
        CHARACTERS[character]["role"] = character.capitalize()
    if "full-name" not in CHARACTERS[character] or CHARACTERS[character]["full-name"] is None:
        CHARACTERS[character]["full-name"] = character.capitalize()

ROLES_TO_CHARACTERS = {
    details["role"]: character for character, details in CHARACTERS.items()
}

STARTING_PLAYER = CARD_LIST["starting-player"]
print(STARTING_PLAYER)

ALL_SUSPECTS = CARD_LIST["suspects"]
suspect_keys = random.sample(ALL_SUSPECTS.keys(), 5)
SUSPECTS = { k: ALL_SUSPECTS[k] for k in suspect_keys }

ALL_LOCATIONS = CARD_LIST["locations"]
location_keys = random.sample(ALL_LOCATIONS.keys(), 5)
LOCATIONS = { k: ALL_LOCATIONS[k] for k in location_keys }

SEARCHING = CARD_LIST["searching"]
CLUES = CARD_LIST["clues"]
