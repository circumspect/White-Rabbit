from pathlib import Path
# 3rd-party
import discord

CHARACTERS = {
    "charlie": "Charlie Barnes",
    "dakota": "Dakota Travis",
    "evan": "Evan Holwell",
    "jack": "Jack Briarwood",
    "julia": "Julia North",
}

# Image
CARD_DIR = Path("Images/Cards")
RESOURCE_DIR = Path("Images/Player Resources")
CHARACTER_IMAGE_DIR = CARD_DIR / "Characters"
SUSPECT_IMAGE_DIR = CARD_DIR / "Suspects"
LOCATION_IMAGE_DIR = CARD_DIR / "Locations"

GAME_LENGTH = 90 * 60
# How often the bot should check the timer
TIMER_GAP = 10


class Data:
    def __init__(self, guild):
        self.guild = guild
        self.setup = False
        self.started = False
        self.show_timer = False
        self.char_roles = {
            role.name: role
            for role in guild.roles
            if role.name.lower() in CHARACTERS and role.members
        }
