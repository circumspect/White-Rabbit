import random

from utils import miscutils, dirs, errors
from utils.localization import LOCALIZATION_DATA

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

# Message to send when reminding player
TEN_MIN_REMINDER_TIME = 15
TEN_MIN_REMINDER_TEXT = LOCALIZATION_DATA["messages"]["TenMinuteReminder"]

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
    80: "suspect",
    70: "location",
    60: "suspect",
    50: "location",
    45: ("suspect", "location", "location"),
    40: "suspect",
    35: "location",
    30: "suspect-drawn",
    20: "location-drawn",
}


TIMER_AUDIO = dirs.RESOURCE_DIR / "Alice.mp3"

# Easy access filepaths
MASTER_PATHS = {
    "guide": miscutils.get_image(dirs.PLAYER_RESOURCE_DIR, "Guide"),
    "character_sheet": miscutils.get_image(dirs.PLAYER_RESOURCE_DIR, "Character-Sheet"),
    "intro": miscutils.get_image(dirs.CARD_DIR / "misc", "Introduction"),
    "debrief": miscutils.get_image(dirs.CARD_DIR / "misc", "Debrief"),
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

for character in CHARACTERS:
    MASTER_PATHS[character] = miscutils.get_image(dirs.CHARACTER_IMAGE_DIR, character)
for suspect in SUSPECTS:
    MASTER_PATHS[suspect] = miscutils.get_image(dirs.SUSPECT_IMAGE_DIR, suspect)
for location in LOCATIONS:
    MASTER_PATHS[location] = miscutils.get_image(dirs.LOCATION_IMAGE_DIR, location)


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

        # Settings
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
        self.second_culprit = ""

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

        self.search_cards = list(SEARCHING.keys())

        # Voicemails
        self.voicemails = {}
        for character in CHARACTERS:
            self.voicemails[character] = ""

        # Default level for removing out-of-character messages
        self.ooc_strip_level = 1

        # DO NOT TOUCH
        # How often the bot should check the timer, in seconds
        # Use !timer to change
        self.timer_gap = 10
        # Use !speed when bot is running to set value (DEBUG USE ONLY)
        self.game_speed = 1

        # Find the spectator role
        for role in self.guild.get_roles().values():
            if role.name.title() == LOCALIZATION_DATA["spectator-role"]:
                self.spectator_role = role
                break

    def char_roles(self):
        """
        Returns a dictionary mapping titlecase character names to their
        corresponding roles for all characters currently being played
        """

        unsorted = {
            role.name: role
            for role_id, role in self.guild.get_roles().items()
            if role.name.lower() in CHARACTERS
            and any(
                role_id in member.role_ids
                for member in self.guild.get_members().values()
            )
        }

        return dict(sorted(unsorted.items(), key=lambda item: item[0]))

    def draw_suspect(self, time: int):
        """Picks a suspect given the clue time"""

        clue_type = CLUE_TYPES[time]

        # Check if is tuple and pull the correct type from it
        if isinstance(clue_type, tuple):
            clue_type = clue_type[self.picked_clues[time] - 1]

        if clue_type == "suspect":
            index = random.randint(0, len(self.suspect_pile) - 1)
            self.suspects_drawn[time] = self.suspect_pile.pop(index)
            return self.suspects_drawn[time]
        elif clue_type == "location":
            index = random.randint(0, len(self.location_pile) - 1)
            self.locations_drawn[time] = self.location_pile.pop(index)
            return self.locations_drawn[time]
        elif clue_type == "suspect-drawn":
            culprit = random.choice(list(self.suspects_drawn.values()))
            self.suspects_drawn[time] = culprit
            return culprit
        elif clue_type == "location-drawn":
            final_location = random.choice(list(self.locations_drawn.values()))
            self.locations_drawn[time] = final_location
            return final_location
        else:
            raise ValueError("Unexpected clue type!")

    def assign_clues(self):
        # Stop if fewer than 3 player roles assigned
        if len(self.char_roles()) < 3:
            raise errors.NotEnoughPlayers()
        elif "Charlie" not in self.char_roles():
            raise errors.MissingCharlie()

        clue_buckets = self.generate_clue_buckets(len(self.char_roles()))
        random.shuffle(clue_buckets)

        # Empty buckets
        self.clue_assignments = {}

        # Give bucket with 90 minute card to Charlie Barnes
        for bucket in clue_buckets:
            if 90 in bucket:
                # Charlie's bucket! Willy Wonka sends his regards
                self.clue_assignments["charlie"] = sorted(bucket, reverse=True)
                clue_buckets.remove(bucket)
                break

        # Assign the rest of the buckets randomly
        names = [name.lower() for name in self.char_roles()]
        names.remove("charlie")  # Already assigned
        for name in names:
            self.clue_assignments[name] = sorted(clue_buckets.pop(), reverse=True)

    def generate_clue_buckets(self, player_count: int):
        def _randomize_clues(player_count: int):
            """
            Assigns clues to random buckets
            """

            shuffled_clues = list(CLUE_TIMES)
            random.shuffle(shuffled_clues)

            clue_buckets = [list() for _ in range(player_count)]
            bucket_sizes = BUCKET_SIZES[player_count]
            for i in range(len(bucket_sizes)):
                for _ in range(bucket_sizes[i]):
                    clue_buckets[i].append(shuffled_clues.pop())

            return clue_buckets

        def _test_clue_buckets(player_count: int, clue_buckets):
            """
            Checks clue buckets and returns False if any checks fail
            """

            for bucket in clue_buckets:
                # If three players, make sure Charlie gets the 4 clue bucket
                # This both ensures that each player has the same number of clues
                # (not counting the 90 minute card) and caps the clues on each
                # character page in the PDF export at 3
                if len(bucket) == 4 and 90 not in bucket:
                    return False

                # If four players, make sure Charlie gets three clues so PDF export
                # doesn't look like Charlie has one and someone else has three
                if player_count == 4 and 90 in bucket and len(bucket) == 2:
                    return False

                # Make sure no bucket has clues within 10 minutes of each other
                for i in range(len(bucket)):
                    for j in range(i + 1, len(bucket)):
                        diff = abs(bucket[i] - bucket[j])
                        if diff <= 10:
                            return False

            return True

        while True:
            clue_buckets = _randomize_clues(player_count)
            if _test_clue_buckets(player_count, clue_buckets):
                return clue_buckets

    def shuffle_clues(self):
        for time in CLUE_TIMES:
            self.picked_clues[time] = random.randint(1, 3)

        # Only one card for the 90 minute clue
        self.picked_clues[90] = 1

    async def send_clue(self, time: int):
        # Find character who the clue has been assigned to:
        if not self.picked_clues:
            raise errors.CluesNotShuffled()
        # Check that clues have been assigned
        if not self.clue_assignments:
            raise errors.CluesNotAssigned()

        for name in self.clue_assignments:
            if time in self.clue_assignments[name]:
                character = name
                break
        else:
            raise ValueError("Missing clue")

        # Send clue card
        channel = miscutils.get_text_channels(self.guild)[
            LOCALIZATION_DATA["channels"]["clues"][character]
        ]
        choice = self.picked_clues[time]
        path = miscutils.get_image(dirs.CLUE_DIR / str(time), f"{time}-{choice}")
        miscutils.send_image(channel, path)

        # Send suspect/location card to player's clues channel
        suspect = self.draw_suspect(time)
        path = MASTER_PATHS[suspect]
        miscutils.send_image(channel, path)

        # Send suspect/location card to respective drawn cards channel
        if suspect in SUSPECTS:
            channel = LOCALIZATION_DATA["channels"]["cards"]["suspects-drawn"]
        elif suspect in LOCATIONS:
            channel = LOCALIZATION_DATA["channels"]["cards"]["locations-drawn"]
        else:
            channel = LOCALIZATION_DATA["channels"]["bot-channel"]
        channel = miscutils.get_text_channels(self.guild)[channel]
        # Confirmed culprit/location
        if time <= 30:
            if suspect in SUSPECTS:
                await channel.send(LOCALIZATION_DATA["messages"]["Culprit"])
            elif suspect in LOCATIONS:
                await channel.send(LOCALIZATION_DATA["messages"]["AliceLocation"])

            else:
                print("Something has gone very very wrong.")
                await channel.send(LOCALIZATION_DATA["errors"]["UnknownError"])
        miscutils.send_image(channel, path)

        # Update next_clue unless at end
        if self.next_clue != 20:
            for i in range(len(CLUE_TIMES)):
                if CLUE_TIMES[i] == self.next_clue:
                    self.next_clue = CLUE_TIMES[i + 1]
                    break

    def shuffle_motives(self):
        motives = list(range(1, 6))
        random.shuffle(motives)
        self.motives = dict(zip(motives, CHARACTERS))

    async def send_motives(self):
        if not self.motives:
            raise errors.MotivesUnshuffled()
        for name in CHARACTERS:
            channel = miscutils.get_text_channels(self.guild)[
                LOCALIZATION_DATA["channels"]["clues"][name]
            ]
            motive = self.motives[name]
            miscutils.send_image(
                channel,
                miscutils.get_image(dirs.MOTIVE_DIR, f"Motive-{motive}"),
                self.guild,
            )

    async def send_times(self):
        if not self.clue_assignments:
            raise errors.CluesNotAssigned()
        message = (
            LOCALIZATION_DATA["commands"]["manual"]["print_times"]["ClueTimes"] + "\n"
        )
        message += "\n".join(
            [
                f"{player.title()}: {', '.join(str(x) for x in bucket)}"
                for player, bucket in self.clue_assignments.items()
            ]
        )
        message = miscutils.codeblock(message)

        channel = miscutils.get_text_channels(self.guild)[
            LOCALIZATION_DATA["channels"]["resources"]
        ]
        await channel.send(message)

    async def send_alice(self):
        miscutils.send_image(
            LOCALIZATION_DATA["channels"]["resources"],
            miscutils.get_image(dirs.POSTER_DIR, f"Alice-Briarwood-{self.alice}"),
            self.guild,
        )
