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
    "halvert": "Mr. Halvert",
    "ryan": "Ryan Groggins",
}

LOCATIONS = {
    "barn": "Barn",
    "lighthouse": "Lighthouse",
    "nightclub": "Nightclub",
    "park": "State Park",
    "station": "Train Station",
}

GAME_LENGTH = 90 * 60
# How often the bot should check the timer
TIMER_GAP = 10

# Clue card info
CLUE_TIMES = (90, 80, 70, 60, 50, 45, 40, 35, 30, 20)
BUCKET_SIZES = {3: (3, 3, 4), 4: (2, 2, 3, 3), 5: (2, 2, 2, 2, 2)}
CLUE_TYPES = {80: "suspect", 70: "location", 60: "suspect", 50: "location",
                45: ("suspect", "location", "location"), 40: "suspect", 
                35: "location", 30: "suspect-drawn", 20: "location-drawn"}

class Data:
    def __init__(self, guild):
        self.guild = guild
        self.setup = False
        self.started = False
        self.automatic = False
        self.show_timer = False
        self.stream_music = False

        # Shuffle and assign motive cards
        motives = list(range(1, 6))
        random.shuffle(motives)
        self.motives = {
            character: motive
            for motive, character in zip(motives, CHARACTERS)
        }

        # Create empty clue dicts
        self.clue_assignments = {}
        self.picked_clues = {}

        # Suspects and locations
        suspect_pile = []
        for suspect in SUSPECTS.keys():
            suspect_pile.append(suspect)
            suspect_pile.append(suspect)

        location_pile = []
        for location in LOCATIONS.keys():
            location_pile.append(location)
            location_pile.append(location)

        drawn_suspects = []
        drawn_locations = []

    def char_roles(self):
        unsorted = {
            role.name: role
            for role in self.guild.roles
            if role.name.lower() in CHARACTERS and role.members
        }

        return dict(sorted(unsorted.items(), key=lambda item: item[0]))

