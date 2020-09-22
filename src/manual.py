# Built-in
import asyncio
import random
# 3rd-party
import discord
from discord.ext import commands
# Local
import utils
import gamedata
import utils

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
            print(f"{ctx.author.name} tried to run {ctx.command.name} in automatic mode!")

        return not ctx.game.automatic

    @commands.command()
    async def draw_motive(self, ctx):
        """Draw a motive card"""

        # Make sure player has a character role
        if not ctx.character:
            await ctx.send("You don't have a character role!")
            return
        
        asyncio.create_task(ctx.send("Sending your motive card!"))
        channel = ctx.text_channels[f"{ctx.character}-clues"]
        asyncio.create_task(channel.send(file=discord.File(
            utils.MOTIVE_DIR / f"Motive {ctx.game.motives[ctx.character]}.png"
        )))

    @commands.command()
    async def clue(self, ctx, time: int):
        """
        Draws a clue card given a time

        Ex: !clue 40
        """

        # Check that clue exists at specified time
        if time not in gamedata.CLUE_TIMES:
            asyncio.create_task(ctx.send("No clue card found for that time!"))
            return

        # Check that clues have been assigned
        if not ctx.game.clue_assignments:
            asyncio.create_task(ctx.send("Clues have not been assigned!"))
            return

        # Check if clues have been shuffled:
        if not ctx.game.picked_clues:
            asyncio.create_task(ctx.send("Clues have not been shuffled!"))
            return

        # Check that the person calling the command has the clue
        if time not in ctx.game.clue_assignments[ctx.character]:
            asyncio.create_task(ctx.send("That clue doesn't belong to you!"))
            return

        # Send the clue
        self.send_clue(ctx.game, time)

    def send_clue(self, game, time: int):
        # Send clue based on picked_clues value
        for name in game.clue_assignments:
            if time in game.clue_assignments[name]:
                character = name
                break

        channel = utils.get_text_channels(game.guild)[f"{character}-clues"]
        choice = game.picked_clues[time]
        path = utils.CLUE_DIR / str(time) / f"{time}-{choice}.png"
        self.bot.cogs["Game"].send_image(channel, path)
        suspect = self.draw_suspect(game, time)
        path = utils.MASTER_PATHS[suspect]
        self.bot.cogs["Game"].send_image(channel, path)

    def draw_suspect(self, game, time: int):
        clue_type = gamedata.CLUE_TYPES[time]

        # Check if is tuple and pull the correct type from it
        if type(clue_type) is tuple:
            clue_type = clue_type[game.picked_clues[time]-1]
        
        if clue_type == "suspect":
            index = random.randint(0, len(game.suspect_pile)-1)
            game.suspects_drawn[time] = (game.suspect_pile.pop(index))
            return game.suspects_drawn[time]
        elif clue_type == "location":
            index = random.randint(0, len(game.location_pile)-1)
            game.suspects_drawn[time] = (game.suspect_pile.pop(index))
            return game.suspects_drawn[time]
        elif clue_type == "suspect-drawn":
            culprit = random.choice(game.suspects_drawn.values())
            game.suspects_drawn[time] = culprit
            return culprit
        elif clue_type == "location-drawn":
            final_location = random.choice(game.locations_drawn.values())
            game.locations_drawn[time] = final_location
            return final_location
        else:
            print("Error: Unexpected clue type!")
            return ""

    @commands.command()
    async def shuffle_clues(self, ctx):
        """(Re)shuffles the clue card piles"""

        asyncio.create_task(ctx.send("Shuffling the clues!"))

        for time in gamedata.CLUE_TIMES:
            ctx.game.picked_clues[time] = random.randint(1, 3)
        # Only one card for the 90 minute clue
        ctx.game.picked_clues[90] = 1

        # Console logging
        print("Shuffled clue piles!")
        print(ctx.game.picked_clues)

    @commands.command()
    async def assign_clues(self, ctx):
        """Randomizes and assigns clue times"""

        player_count = len(ctx.game.char_roles())
        # Stop if fewer than 3 player roles assigned
        if player_count < 3:
            await ctx.send("Not enough players!")
            return
        elif "Charlie" not in ctx.game.char_roles():
            await ctx.send("Can't find Charlie!")
            return

        asyncio.create_task(ctx.send("Assigning clue cards!"))

        # Generate clues
        while True:
            clue_buckets = self._randomize_clues(player_count)
            if self._test_clue_buckets(clue_buckets):
                break

        random.shuffle(clue_buckets)

        # Empty buckets
        ctx.game.clue_assignments = {}

        # Give bucket with 90 minute card to Charlie Barnes
        for bucket in clue_buckets:
            if 90 in bucket:
                # Willy Wonka sends his regards
                ctx.game.clue_assignments["charlie"] = sorted(bucket, reverse=True)
                clue_buckets.remove(bucket)
                break

        # Assign the rest of the buckets randomly
        names = [name.lower() for name in ctx.game.char_roles()]
        names.remove("charlie")  # already assigned
        for name in names:
            ctx.game.clue_assignments[name] = sorted(clue_buckets.pop(), reverse=True)

        # Print in a code block
        message = "Clue times:\n"
        message += "\n".join([
            f"{player.title()}: {', '.join(str(x) for x in bucket)}"
            for player, bucket in ctx.game.clue_assignments.items()
        ])
        channel = ctx.text_channels["player-resources"]
        asyncio.create_task(channel.send(f"```{message}```"))

        # Console logging
        print("Randomly assigned clue cards!")
        print(ctx.game.clue_assignments)

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

    def _test_clue_buckets(self, clue_buckets):
        """
        Checks to see if any clue bucket contains two times
        within 10 minutes of each other
        """

        for bucket in clue_buckets:
            for i in range(len(bucket)):
                for j in range(i + 1, len(bucket)):
                    diff = abs(bucket[i] - bucket[j])
                    if diff <= 10:
                        return False

        return True


def setup(bot):
    bot.add_cog(Manual(bot))
