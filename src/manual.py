# Built-in
import asyncio
import random
# 3rd-party
import discord
from discord.ext import commands
# Local
import filepaths
import gamedata

class Manual(commands.Cog):
    """
    A set of commands for running the game in manual mode
    
    If in automatic mode, the bot will call these at the appropriate times
    without user input
    """

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.game.automatic:
            await ctx.send("Not in manual mode!")
        return ctx.game.automatic

    @commands.command()
    async def draw_motive(self, ctx):
        """Draw a motive card"""

        if not ctx.character:
            await ctx.send("You don't have a character role!")
            return
        channel = ctx.text_channels[f"{ctx.character}-clues"]
        asyncio.create_task(channel.send(file=discord.File(
            filepaths.MOTIVE_DIR / f"Motive {ctx.game.motives[ctx.character]}.png"
        )))
    
    @commands.command()
    async def clue(self, ctx, time: int):
        """Draws a clue card given a time"""
        
        # Check that clue exists at specified time
        if time not in gamedata.CLUE_TIMES:
            asyncio.create_task(ctx.send("No clue card found for that time!"))
            return
        
        # Check that clues have been assigned
        if not ctx.game.clue_buckets:
            asyncio.create_task(ctx.send("Clues have not been assigned!"))
            return
        
        # Check that the person calling the command has the clue
        if time not in ctx.game.clue_buckets[ctx.character]:
            asyncio.create_task(ctx.send("That clue doesn't belong to you!"))
            return
        
        # Send random clue
        channel = ctx.text_channels[f"{ctx.character}-clues"]
        asyncio.create_task(channel.send("CLUE GOES HERE"))

    @ commands.command()
    async def shuffle_clues(self, ctx):
        """(Re)shuffles the clue card piles"""

        ctx.game.picked_clues = {}
        for time in gamedata.CLUE_TIMES:
            ctx.game.picked_clues[time] = random.randint(1, 3)
        
        # Console logging
        print("Reshuffled clue piles!")
        print(ctx.game.picked_clues)


    @commands.command()
    async def assign_clues(self, ctx):
        """Randomizes and assigns clue times"""
        player_count = len(ctx.game.char_roles())
        # Stop if fewer than 3 player roles assigned
        if player_count < 3:
            await ctx.send("Not enough players!")
            return

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
                ctx.game.clue_assignments["charlie"] = bucket
                clue_buckets.remove(bucket)
                break

        # Assign the rest of the buckets randomly
        names = [name.lower() for name in ctx.game.char_roles()]
        names.remove("charlie")  # already assigned
        for name in names:
            ctx.game.clue_assignments[name] = clue_buckets.pop().sort(reverse=True)

        # Print in a code block
        message = "\n".join([
            f"{player.title()}: {', '.join(str(x) for x in bucket)}"
            for player, bucket in ctx.game.clue_assignments.items()
        ])
        asyncio.create_task(ctx.send(f"```{message}```"))

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
