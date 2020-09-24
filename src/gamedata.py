# Built-in
import random

CHARACTERS = {
    "charlie": "Charlie Barnes",
    "dakota": "Dakota Travis",
    "evan": "Evan Holwell",
    "jack": "Jack Briarwood",
    "julia": "Julia North",
}

SUSPECTS = {
    "bria": "Bria Brown",
    "cj": "CJ Wallace",
    "david": "David Nelson",
    "halvert": "Mr Halvert",
    "ryan": "Ryan Groggins",
}

LOCATIONS = {
    "barn": "Barn",
    "lighthouse": "Lighthouse",
    "nightclub": "Nightclub",
    "park": "State Park",
    "station": "Train Station",
}

# Game length, in seconds
GAME_LENGTH = 90 * 60
# Max game speed
MAX_SPEED = 30
# Minimum seconds between timer messages
MIN_TIMER_GAP = 10

# How many minutes after the clue time has passed before reminding the player
# when running in manual mode
REMINDER_BUFFER = 2

# Clue card info
CLUE_TIMES = (90, 80, 70, 60, 50, 45, 40, 35, 30, 20)
BUCKET_SIZES = {3: (3, 3, 4), 4: (2, 2, 3, 3), 5: (2, 2, 2, 2, 2)}
CLUE_TYPES = {
    80: "suspect", 70: "location", 60: "suspect", 50: "location",
    45: ("suspect", "location", "location"), 40: "suspect",
    35: "location", 30: "suspect-drawn", 20: "location-drawn"
}

class Data:
    def __init__(self, guild):
        self.guild = guild
        self.init = False
        self.setup = False
        self.started = False
        self.automatic = True
        self.show_timer = False
        self.stream_music = False
        self.motives = {}
        self.ten_char = None
        self.three_flip = False
        self.second_culprit = False

        # How often the bot should check the timer, in seconds
        self.timer_gap = 10

        # DO NOT CHANGE
        # Use !speed when bot is running to set value (DEBUG USE ONLY)
        self.game_speed = 1

        # Clue vars
        self.clue_assignments = {}
        self.picked_clues = {}
        self.endings = {}
        for i in range(1, 4):
            # Enable all endings
            self.endings[i] = True

        # Suspects and locations
        self.suspect_pile = []
        for suspect in SUSPECTS.keys():
            self.suspect_pile.append(suspect)
            self.suspect_pile.append(suspect)

        self.location_pile = []
        for location in LOCATIONS.keys():
            self.location_pile.append(location)
            self.location_pile.append(location)

        self.suspects_drawn = {}
        self.locations_drawn = {}
        self.next_clue = 80

    def char_roles(self):
        unsorted = {
            role.name: role
            for role in self.guild.roles
            if role.name.lower() in CHARACTERS and role.members
        }

        return dict(sorted(unsorted.items(), key=lambda item: item[0]))
