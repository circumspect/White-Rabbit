# Built-in
import asyncio
import random
# 3rd-party
from discord.ext import commands
# Local
from data import cards, constants, dirs, filepaths, gamedata
from data.cards import CLUES, STARTING_PLAYER
from data.localization import LOCALIZATION_DATA
import utils

loc = LOCALIZATION_DATA["commands"]["manual"]


class Manual(commands.Cog):
    """
    A set of commands for running the game in manual mode

    If in automatic mode, the bot will call these at the appropriate times
    without user input
    """

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        ctx.game = self.bot.games.setdefault(ctx.guild.id, gamedata.Data(ctx.guild))
        # Console logging
        if ctx.game.automatic:
            print(f"{constants.WARNING_PREFIX}{ctx.author.name} tried to run {self.bot.command_prefix}{ctx.command.name} in automatic mode!")

        return not ctx.game.automatic

    @commands.command(
        name=loc["alice"]["name"],
        aliases=loc["alice"]["aliases"],
        description=loc["alice"]["description"]
    )
    async def alice(self, ctx, choice: int = 0):
        """
        Sends a specified Alice poster, or a random one if no argument is
        passed

        This will also update the Alice value in the game data.
        """

        if choice < 0 or choice > 10:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["UserInputError"]))
            return

        if not choice:
            choice = random.randint(1, 10)

        ctx.game.alice = choice

        alice = utils.get_image(dirs.POSTER_DIR, f"Alice-Briarwood-{ctx.game.alice}")
        await utils.send_image(LOCALIZATION_DATA["channels"]["resources"], alice, ctx)

    @commands.command(
        name=loc["shuffle_motives"]["name"],
        aliases=loc["shuffle_motives"]["aliases"],
        description=loc["shuffle_motives"]["description"]
    )
    async def shuffle_motives(self, ctx):
        """Shuffle and assign motive cards"""

        if not ctx.game.automatic:
            asyncio.create_task(ctx.send(loc["shuffle_motives"]["Shuffling"]))

        motives = list(range(1, 6))
        random.shuffle(motives)
        ctx.game.motives = {
            character.lower(): motive
            for character, motive in zip(ctx.game.char_roles(), motives)
        }

        # Console logging
        print(f"{constants.INFO_PREFIX}Shuffled motives!")
        print(ctx.game.motives)

    @commands.command(
        name=loc["send_motives"]["name"],
        aliases=loc["send_motives"]["aliases"],
        description=loc["send_motives"]["description"]
    )
    async def send_motives(self, ctx):
        """Distributes motive cards"""

        if not ctx.game.motives:
            asyncio.create_task(ctx.send(loc["send_motives"]["NeedToShuffle"]))
            return

        async_tasks = []
        for character, motive in ctx.game.motives.items():
            channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["clues"][character]]
            async_tasks.append(
                utils.send_image(
                    channel,
                    utils.get_image(dirs.MOTIVE_DIR, f"Motive-{motive}"),
                    ctx
                )
            )

        await asyncio.gather(*async_tasks)

    @commands.command(
        name=loc["clue"]["name"],
        aliases=loc["clue"]["aliases"],
        description=loc["clue"]["description"]
    )
    async def clue(self, ctx, time: int):
        """
        Draws a clue card given a time

        Ex: !clue 40
        """

        # Check that clue exists at specified time
        if time not in gamedata.CLUE_TIMES:
            asyncio.create_task(ctx.send(loc["clue"]["ClueNotFound"]))
            return

        # Check that clues have been assigned
        if not ctx.game.clue_assignments:
            asyncio.create_task(ctx.send(loc["clue"]["CluesNotAssigned"]))
            return

        # Check if clues have been shuffled:
        if not ctx.game.picked_clues:
            asyncio.create_task(ctx.send(loc["clue"]["CluesNotShuffled"]))
            return

        # This check is disabled to allow more flexibility when running in
        # manual mode if players want to decide who gets what clue. If you
        # wish ensure that players cannot draw each other's clues, uncomment
        # out the lines below
        #
        # # Check that the person calling the command has the clue
        # # Ignores this check for the 10 minute clue because that one
        # # is assigned manually anyway
        # if time != 10 and time not in ctx.game.clue_assignments[ctx.character]:
        #     asyncio.create_task(ctx.send(loc["clue"]["NotYourClue"]))
        #     return

        # Send the clue
        await self.send_clue(ctx, time)

    async def send_clue(self, ctx, time: int):
        # Sends clue based on picked_clues value

        # Find character who the clue has been assigned to
        for name in ctx.game.clue_assignments:
            if time in ctx.game.clue_assignments[name]:
                character = name
                break
        else:
            raise ValueError("Missing clue")

        # Send clue card
        channel = utils.get_text_channels(ctx.game.guild)[LOCALIZATION_DATA["channels"]["clues"][character]]
        choice = ctx.game.picked_clues[time]
        path = utils.get_image(dirs.CLUE_DIR / str(time), f"{time}-{choice}")
        await utils.send_image(channel, path)

        # Send suspect/location card to player's clues channel
        suspect = self.draw_suspect(ctx, time)
        path = filepaths.MASTER_PATHS[suspect]
        await utils.send_image(channel, path)

        # Send suspect/location card to respective drawn cards channel
        if suspect in cards.SUSPECTS:
            channel = LOCALIZATION_DATA["channels"]["cards"]["suspects-drawn"]
        elif suspect in cards.LOCATIONS:
            channel = LOCALIZATION_DATA["channels"]["cards"]["locations-drawn"]
        else:
            channel = LOCALIZATION_DATA["channels"]["bot-channel"]
        channel = utils.get_text_channels(ctx.game.guild)[channel]
        # Confirmed culprit/location
        if time <= 30:
            if suspect in cards.SUSPECTS:
                await channel.send(LOCALIZATION_DATA["messages"]["Culprit"])
            elif suspect in cards.LOCATIONS:
                await channel.send(LOCALIZATION_DATA["messages"]["AliceLocation"])
            else:
                print("Something has gone very very wrong.")
                await channel.send(LOCALIZATION_DATA["errors"]["UnknownError"])
        await utils.send_image(channel, path)

        # Update next_clue unless at end
        if ctx.game.next_clue != 20:
            for i in range(len(gamedata.CLUE_TIMES)):
                if gamedata.CLUE_TIMES[i] == ctx.game.next_clue:
                    ctx.game.next_clue = gamedata.CLUE_TIMES[i+1]
                    break

    def draw_suspect(self, ctx, time: int):
        """Picks a suspect given the clue time"""

        clue_type = gamedata.CLUE_TYPES[time]

        # Check if is tuple and pull the correct type from it
        if isinstance(clue_type, tuple):
            clue_type = clue_type[ctx.game.picked_clues[time]-1]

        if clue_type == "suspect":
            index = random.randint(0, len(ctx.game.suspect_pile)-1)
            ctx.game.suspects_drawn[time] = (ctx.game.suspect_pile.pop(index))
            return ctx.game.suspects_drawn[time]
        elif clue_type == "location":
            index = random.randint(0, len(ctx.game.location_pile)-1)
            ctx.game.locations_drawn[time] = (ctx.game.location_pile.pop(index))
            return ctx.game.locations_drawn[time]
        elif clue_type == "suspect-drawn":
            culprit = random.choice(list(ctx.game.suspects_drawn.values()))
            ctx.game.suspects_drawn[time] = culprit
            return culprit
        elif clue_type == "location-drawn":
            final_location = random.choice(list(ctx.game.locations_drawn.values()))
            ctx.game.locations_drawn[time] = final_location
            return final_location
        else:
            raise ValueError("Unexpected clue type!")

    @commands.command(
        name=loc["shuffle_clues"]["name"],
        aliases=loc["shuffle_clues"]["aliases"],
        description=loc["shuffle_clues"]["description"]
    )
    async def shuffle_clues(self, ctx):
        """(Re)shuffles the clue card piles"""

        if not ctx.game.automatic:
            asyncio.create_task(
                ctx.send(loc["shuffle_clues"]["ShufflingClues"])
            )

        for time in gamedata.CLUE_TIMES:
            if time != 90:
                ctx.game.picked_clues[time] = random.choice([*CLUES[time].keys()])

        # Only one card for the 90 minute clue
        ctx.game.picked_clues[90] = random.choice([*CLUES[90][STARTING_PLAYER].keys()])

        # Console logging
        print(f"{constants.INFO_PREFIX}Shuffled clue piles!")
        print(ctx.game.picked_clues)

    @commands.command(
        name=loc["assign_times"]["name"],
        aliases=loc["assign_times"]["aliases"],
        description=loc["assign_times"]["description"]
    )
    async def assign_times(self, ctx):
        """Randomizes and assigns clue times"""

        player_count = len(ctx.game.char_roles())
        # Stop if fewer than 3 player roles assigned
        if player_count < 3:
            asyncio.create_task(ctx.send(loc["errors"]["NotEnoughPlayers"]))
            return

        # Can't play without 90 clue player
        elif cards.CHARACTERS[STARTING_PLAYER].role not in ctx.game.char_roles():
            asyncio.create_task(ctx.send(loc["errors"]["MissingCharlie"]))
            return

        if not ctx.game.automatic:
            asyncio.create_task(
                ctx.send(loc["assign_clues"]["AssigningClues"])
            )

        # Generate clues
        while True:
            clue_buckets = self._randomize_clues(player_count)
            if self._test_clue_buckets(ctx, clue_buckets):
                break

        random.shuffle(clue_buckets)

        # Empty buckets
        ctx.game.clue_assignments = {}

        # Give bucket with 90 minute card to starting player
        for bucket in clue_buckets:
            if 90 in bucket:
                ctx.game.clue_assignments[STARTING_PLAYER] = sorted(bucket, reverse=True)
                clue_buckets.remove(bucket)
                break

        # Assign the rest of the buckets randomly
        names = [name.lower() for name in ctx.game.char_roles()]
        names.remove(STARTING_PLAYER)  # Already assigned
        for name in names:
            ctx.game.clue_assignments[name] = sorted(clue_buckets.pop(), reverse=True)

        # Console logging
        print(f"{constants.INFO_PREFIX}Assigned clue cards!")
        print(ctx.game.clue_assignments)

    @commands.command(
        name=loc["print_times"]["name"],
        aliases=loc["print_times"]["aliases"],
        description=loc["print_times"]["description"]
    )
    async def print_times(self, ctx):
        """
        Print out clue assignments in a code block
        """

        message = loc["print_times"]["ClueTimes"] + "\n"
        message += "\n".join([
            f"{player.title()}: {', '.join(str(x) for x in bucket)}"
            for player, bucket in ctx.game.clue_assignments.items()
        ])
        message = utils.codeblock(message)

        channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["resources"]]
        asyncio.create_task(channel.send(message))

    def _randomize_clues(self, player_count: int):
        """
        Assigns clues to random buckets
        """

        shuffled_clues = list(gamedata.CLUE_TIMES)
        random.shuffle(shuffled_clues)

        clue_buckets = [list() for _ in range(player_count)]
        bucket_sizes = gamedata.BUCKET_SIZES[player_count]
        for i in range(len(bucket_sizes)):
            for _ in range(bucket_sizes[i]):
                clue_buckets[i].append(shuffled_clues.pop())

        return clue_buckets

    def _test_clue_buckets(self, ctx, clue_buckets):
        """
        Checks clue buckets and returns False if any checks fail
        """

        for bucket in clue_buckets:
            # If three players, make sure starting player gets the 4 clue bucket
            # This both ensures that each player has the same number of clues
            # (not counting the 90 minute card) and caps the clues on each
            # character page in the PDF export at 3
            if len(bucket) == 4 and 90 not in bucket:
                return False

            # If four players, make sure starting player gets three clues so PDF export
            # doesn't look like they has have and someone else has three
            if len(ctx.game.char_roles()) == 4 and 90 in bucket and len(bucket) == 2:
                return False

            # Make sure no bucket has clues within 10 minutes of each other
            for i in range(len(bucket)):
                for j in range(i + 1, len(bucket)):
                    diff = abs(bucket[i] - bucket[j])
                    if diff <= 10:
                        return False

        return True


async def setup(bot):
    await bot.add_cog(Manual(bot))
