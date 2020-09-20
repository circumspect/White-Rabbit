# Built-in
import asyncio
import random
import time
from pathlib import Path
import typing
# 3rd-party
import discord
from discord.ext import commands, tasks
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
            CARD_DIR / "Motives" / f"Motive {ctx.game.motives[character]}.png"
        )))

    def get_char(self, member: discord.Member):
        for role in member.roles:
            if role.name.lower() in gamedata.CHARACTERS:
                return role.name.lower()

    @commands.command()
    async def shuffle_clues(self, ctx):
        """Randomizes and assigns clue times"""

        # Stop if fewer than 3 player roles assigned
        if len(ctx.game.char_roles()) < 3:
            await ctx.send("Not enough players!")
            return

        player_count = len(ctx.game.char_roles())
        acceptable = False
        while not acceptable:
            clue_buckets = self.randomize_clues(player_count)
            acceptable = self.test_clue_buckets(clue_buckets)

        # Give bucket with 90 minute card to Charlie Barnes
        for i in range(len(clue_buckets)):
            for time in clue_buckets[i]:
                if time == 90:
                    charlie_bucket = i # Willy Wonka sends his regards

        bucket_assignments = {}
        bucket_assignments["charlie"] = clue_buckets.pop(charlie_bucket)
        
        # Assign the rest of the buckets randomly
        names = list(ctx.game.char_roles().keys())
        names = [item.lower() for item in names]
        names.pop(0) # Need to remove charlie from list
        random.shuffle(clue_buckets)
        for name in names:
            bucket_assignments[name] = clue_buckets.pop()
        
        # Print in a code block
        message = "```"
        for player in bucket_assignments:
            bucket_assignments[player].sort(reverse=True)
            clues = player.title() + ": " + ", ".join(str(bucket_assignments[player][x]) for x in range(len(bucket_assignments[player]))) + "\n"
            message += clues
        
        message += "```"
        asyncio.create_task(ctx.send(message))

        # Console logging
        print("Randomly assigned clue cards!")
        print(bucket_assignments)
        
    def randomize_clues(self, player_count: int):
        """
        Assigns clues to random buckets
        """
        
        shuffled_clues = list(gamedata.CLUE_TIMES)
        random.shuffle(shuffled_clues)
        clue_buckets = []
        for i in range(player_count):
            clue_buckets.append([])
        for i in range(len(gamedata.BUCKET_SIZES[player_count])):
            for _ in range(gamedata.BUCKET_SIZES[player_count][i]):
                clue_buckets[i].append(shuffled_clues.pop())

        return clue_buckets


    def test_clue_buckets(self, clue_buckets):
        """
        Checks to see if any clue bucket contains two times 
        within 10 minutes of each other
        """

        for bucket in range(len(clue_buckets)):
            for i in range(len(clue_buckets[bucket])):
                start = i+1
                end = len(clue_buckets[bucket])
                for j in range(start, end):
                    diff = clue_buckets[bucket][i]-clue_buckets[bucket][j]
                    diff = abs(diff)
                    if diff <= 10:
                        return False
        
        return True

def setup(bot):
    bot.add_cog(Manual(bot))