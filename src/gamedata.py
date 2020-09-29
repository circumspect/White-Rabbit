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

SEARCHING = {
    "10k": "10000 Dollars",
    "alcohol": "Bottle of Alcohol",
    "blade": "Broken Switchblade",
    "blood": "Drops of Blood",
    "firearm": "Firearm",
    "followed": "Followed",
    "mask": "Mask",
    "van": "White Van",
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

        # Status
        self.init = False
        self.setup = False
        self.start_time = None

        self.ten_char = None
        self.three_flip = False
        self.second_culprit = False


        # Setings
        self.automatic = True
        self.show_timer = False
        self.stream_music = False


        # Enabled endings
        self.endings = {}
        for i in range(1, 4):
            # Enable all endings
            self.endings[i] = True


        # Game data
        self.alice = 0
        self.motives = {}
        self.clue_assignments = {}
        self.picked_clues = {}

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

        # Searching
        self.searching = {}
        for character in CHARACTERS:
            self.searching[character] = []
        
        # Voicemails
        self.voicemails = {}
        for character in CHARACTERS:
            self.voicemails[character] = ""

        # PDF export values
        self.ooc_strip = 1

        # DO NOT TOUCH
        # How often the bot should check the timer, in seconds
        # Use !timer to change
        self.timer_gap = 10
        # Use !speed when bot is running to set value (DEBUG USE ONLY)
        self.game_speed = 1


    def char_roles(self):
        unsorted = {
            role.name: role
            for role in self.guild.roles
            if role.name.lower() in CHARACTERS and role.members
        }

        return dict(sorted(unsorted.items(), key=lambda item: item[0]))
