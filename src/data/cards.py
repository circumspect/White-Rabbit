# Built-in
import envvars
import random
import yaml
# Local
from data.card_types import *
from rabbit import WHITE_RABBIT_DIR


CARD_LIST_DIR = WHITE_RABBIT_DIR / "card_lists"
EXPANSION_DIR = CARD_LIST_DIR / "expansions"
PLAYSET_DIR = CARD_LIST_DIR / "playsets"

expansions: List[str] = []
with open(PLAYSET_DIR / f"{envvars.get_env_var('WHITE_RABBIT_PLAYSET')}.playset", "r") as f:
    for line in f:
        line = line.strip()
        if line:
            expansions.append(line)

for expansion in expansions:
    with open(EXPANSION_DIR / f"{expansion}.yaml", "r") as f:
        CARD_LIST = yaml.safe_load(f)

CHARACTERS: Dict[str, Character] = { k: Character(k, v) for k, v in CARD_LIST["characters"].items() }
ROLES_TO_NAMES = { v.role: v.name for _, v in CHARACTERS.items() }

STARTING_PLAYER = CARD_LIST["starting-player"]

ALL_SUSPECTS: Dict[str, Suspect] = { k: Suspect(k, v) for k, v in CARD_LIST["suspects"].items() }
suspect_keys = random.sample(ALL_SUSPECTS.keys(), 5)
SUSPECTS = { k: ALL_SUSPECTS[k] for k in suspect_keys }

ALL_LOCATIONS: Dict[str, Location] = { k: Location(k, v) for k, v in CARD_LIST["locations"].items() }
location_keys = random.sample(ALL_LOCATIONS.keys(), 5)
LOCATIONS = { k: ALL_LOCATIONS[k] for k in location_keys }

SEARCHING: Dict[str, Searching] = { k: Searching(k, v) for k, v in CARD_LIST["searching"].items() }
CLUES = CARD_LIST["clues"]
