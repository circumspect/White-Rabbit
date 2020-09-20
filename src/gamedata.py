import discord
import random
from pathlib import Path

CHARACTERS = {
    "charlie": "Charlie Barnes",
    "dakota": "Dakota Travis",
    "evan": "Evan Holwell",
    "jack": "Jack Briarwood",
    "julia": "Julia North",
}

IMAGE_DIR = Path("Images")
CARD_DIR = IMAGE_DIR / "Cards"
RESOURCE_DIR = IMAGE_DIR / "Player Resources"
CHARACTER_IMAGE_DIR = CARD_DIR / "Characters"
SUSPECT_IMAGE_DIR = CARD_DIR / "Suspects"
LOCATION_IMAGE_DIR = CARD_DIR / "Locations"
CLUE_DIR = CARD_DIR / "Clues"

GAME_LENGTH = 90 * 60
# How often the bot should check the timer
TIMER_GAP = 10

# Times to send clue cards
CLUE_TIMES = (90, 80, 70, 60, 50, 45, 40, 35, 30, 20)
BUCKET_SIZES = {3: (3, 3, 4), 4: (2, 2, 3, 3), 5: (2, 2, 2, 2, 2)}


class Data:
    def __init__(self, guild):
        self.guild = guild
        self.setup = False
        self.started = False
        self.automatic = False
        self.show_timer = False

        motives = list(range(1, 6))
        random.shuffle(motives)
        self.motives = {
            character: motive
            for motive, character in zip(motives, CHARACTERS)
        }

    def char_roles(self):
        unsorted = {
            role.name: role
            for role in self.guild.roles
            if role.name.lower() in CHARACTERS and role.members
        }

        return dict(sorted(unsorted.items(), key=lambda item: item[0]))
