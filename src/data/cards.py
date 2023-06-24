# Built-in
from typing import Dict
import envvars
import random
import sys
import yaml

import requests

# Local
from data.card_types import Character, Location, Suspect, Searching
from rabbit import WHITE_RABBIT_DIR
import utils


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


with open(PLAYSET_DIR / f"{envvars.PLAYSET}.yaml", "r") as f:
    data = yaml.safe_load(f)
    STARTING_PLAYER = data["starting-player"]
    expansions = data["expansions"]

CARD_LIST = None
CHARACTERS: Dict[str, Character] = {}
ALL_SUSPECTS: Dict[str, Suspect] = {}
ALL_LOCATIONS: Dict[str, Location] = {}
SEARCHING: Dict[str, Searching] = {}

for expansion in expansions:
    expansion_file = EXPANSION_DIR / f"{expansion}.yaml"
    if expansion_file.exists():
        with open(expansion_file, "r") as f:
            cards = yaml.safe_load(f)
    else:
        manifest_url =  utils.get_expansion_url(expansion) + "/manifest.yaml"
        response = requests.get(manifest_url)
        cards = yaml.safe_load(response.text)
    if cards is None:
        continue

    if CARD_LIST is None:
        CARD_LIST = cards
    else:
        merge(CARD_LIST, cards)
        for name, data in CARD_LIST["characters"].items():
            if name not in CHARACTERS:
                CHARACTERS[name] = Character(name, expansion, data)

        for name, description in CARD_LIST["suspects"].items():
            if name not in ALL_SUSPECTS:
                ALL_SUSPECTS[name] = Suspect(name, expansion, description)

        for name, description in CARD_LIST["locations"].items():
            if name not in ALL_LOCATIONS:
                ALL_LOCATIONS[name] = Location(name, expansion, description)

        for name, description in CARD_LIST["searching"].items():
            if name not in SEARCHING:
                SEARCHING[name] = Searching(name, expansion, description)


if CARD_LIST is None:
    sys.exit("No expansions loaded!")

ROLES_TO_NAMES = { v.role: v.name for _, v in CHARACTERS.items() }

suspect_keys = random.sample(list(ALL_SUSPECTS), 5)
SUSPECTS = { k: ALL_SUSPECTS[k] for k in suspect_keys }

location_keys = random.sample(list(ALL_LOCATIONS), 5)
LOCATIONS = { k: ALL_LOCATIONS[k] for k in location_keys }

CLUES = CARD_LIST["clues"]

assert STARTING_PLAYER in CLUES[90]
