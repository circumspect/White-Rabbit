import dirs
import gamedata
import utils

DEV_ID_FILE = dirs.WHITE_RABBIT_DIR / "dev_ids.txt"

# Easy access filepaths
MASTER_PATHS = {
    "guide": utils.get_image(dirs.PLAYER_RESOURCE_DIR, "Guide"),
    "character_sheet": utils.get_image(dirs.PLAYER_RESOURCE_DIR, "Character-Sheet"),
    "intro": utils.get_image(dirs.CARD_DIR / "misc", "Introduction"),
    "debrief": utils.get_image(dirs.CARD_DIR / "misc", "Debrief"),
}

LEGACY_FILENAMES = {
    "mr. halvert": "halvert",
    "train-station": "station",
    # Searching cards
    "10000-dollars": "10k",
    "bottle-of-alcohol": "alcohol",
    "broken-switchblade": "blade",
    "drops-of-blood": "blood",
    "white-van": "van",
}

for character in gamedata.CHARACTERS:
    MASTER_PATHS[character] = utils.get_image(dirs.CHARACTER_IMAGE_DIR, character)
for suspect in gamedata.SUSPECTS:
    MASTER_PATHS[suspect] = utils.get_image(dirs.SUSPECT_IMAGE_DIR, suspect)
for location in gamedata.LOCATIONS:
    MASTER_PATHS[location] = utils.get_image(dirs.LOCATION_IMAGE_DIR, location)
