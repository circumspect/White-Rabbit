# Built-in
import envvars
import random
import yaml
# Local
from data.card_types import *
from rabbit import WHITE_RABBIT_DIR


CARD_LIST_DIR = WHITE_RABBIT_DIR / "card_lists"

with open(CARD_LIST_DIR / f"{envvars.get_env_var('WHITE_RABBIT_CARD_LIST')}.yaml", "r") as f:
    CARD_LIST = yaml.safe_load(f)

CHARACTERS: Dict[str, Character] = { k: Character(k, v) for k, v in CARD_LIST["characters"].items() }
ROLES_TO_NAMES = { v.role: v.name for _, v in CHARACTERS.items() }

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
