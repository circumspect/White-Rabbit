# Built-in
from typing import Dict
import envvars
import random
import sys
import yaml
# Local
from data.card_types import Character, Location, Suspect, Searching
from rabbit import WHITE_RABBIT_DIR


CARD_LIST_DIR = WHITE_RABBIT_DIR / "card_lists"
EXPANSION_DIR = CARD_LIST_DIR / "expansions"
PLAYSET_DIR = CARD_LIST_DIR / "playsets"


# https://stackoverflow.com/a/7205107
def merge(a, b, path=None):
    "merges b into a"
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


with open(PLAYSET_DIR / f"{envvars.get_env_var('WHITE_RABBIT_PLAYSET')}.yaml", "r") as f:
    data = yaml.safe_load(f)
    STARTING_PLAYER = data["starting-player"]
    expansions = data["expansions"]

CARD_LIST = None
for expansion in expansions:
    expansion_file = EXPANSION_DIR / f"{expansion}.yaml"
    with open(expansion_file, "r") as f:
        cards = yaml.safe_load(f)
        if cards is None:
            continue

        if CARD_LIST is None:
            CARD_LIST = cards
        else:
            merge(CARD_LIST, cards)

if CARD_LIST is None:
    sys.exit("No expansions loaded!")

CHARACTERS: Dict[str, Character] = {
    k: Character(k, v) for k, v in CARD_LIST["characters"].items()
}
ROLES_TO_NAMES = { v.role: v.name for _, v in CHARACTERS.items() }

ALL_SUSPECTS: Dict[str, Suspect] = {
    k: Suspect(k, v) for k, v in CARD_LIST["suspects"].items()
}
suspect_keys = random.sample(list(ALL_SUSPECTS), 5)
SUSPECTS = { k: ALL_SUSPECTS[k] for k in suspect_keys }

ALL_LOCATIONS: Dict[str, Location] = {
    k: Location(k, v) for k, v in CARD_LIST["locations"].items()
}
location_keys = random.sample(list(ALL_LOCATIONS), 5)
LOCATIONS = { k: ALL_LOCATIONS[k] for k in location_keys }

SEARCHING: Dict[str, Searching] = {
    k: Searching(k, v) for k, v in CARD_LIST["searching"].items()
}
CLUES = CARD_LIST["clues"]

assert STARTING_PLAYER in CLUES[90]
