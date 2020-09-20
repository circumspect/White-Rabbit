# Built-in
import asyncio
import random
# 3rd-party
import discord
from discord.ext import commands
# Local
import gamedata


class Manual(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if ctx.game.automatic:
            await ctx.send("Not in manual mode!")
        return ctx.game.automatic

    @commands.command()
    async def draw_motive(self, ctx):
        """Draw a motive card - manual mode only"""

        character = self.get_char(ctx.author)
        if not character:
            await ctx.send("You don't have a character role!")
            return
        channel = ctx.text_channels[f"{character}-clues"]
        asyncio.create_task(channel.send(file=discord.File(
            gamedata.CARD_DIR / "Motives" / f"Motive {ctx.game.motives[character]}.png"
        )))

    def get_char(self, member: discord.Member):
        for role in member.roles:
            if role.name.lower() in gamedata.CHARACTERS:
                return role.name.lower()

    @commands.command()
    async def shuffle_clues(self, ctx):
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

        # Assign buckets
        bucket_assignments = {}

        # Give bucket with 90 minute card to Charlie Barnes
        for bucket in clue_buckets:
            if 90 in bucket:
                bucket_assignments["charlie"] = bucket  # Willy Wonka sends his regards
                clue_buckets.remove(bucket)
                break

        # Assign the rest of the buckets randomly
        names = [name.lower() for name in ctx.game.char_roles()]
        names.remove("charlie")  # already assigned
        for name in names:
            bucket_assignments[name] = clue_buckets.pop().sort(reverse=True)

        # Print in a code block
        message = "\n".join([
            f"{player.title()}: {', '.join(str(x) for x in bucket)}"
            for player, bucket in bucket_assignments.items()
        ])
        asyncio.create_task(ctx.send(f"```{message}```"))

        # Console logging
        print("Randomly assigned clue cards!")
        print(bucket_assignments)

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
