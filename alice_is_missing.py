import discord
import time
import random
import asyncio
from discord.ext import commands, tasks


class AliceIsMissing(commands.Cog):
    characters = (
        "charlie barnes", "dakota travis",
        "evan holwell", "jack briarwood", "julia north"
    )
    game_length = 90 * 60

    def __init__(self, bot):
        self.bot = bot
        self.setup = False

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        self.text_channels = {
            channel.name: channel
            for channel in self.bot.guilds[0].text_channels
        }
        print(f"Bot has logged in as {self.bot}")

    @commands.command()
    async def start(self, ctx):
        if not self.setup:
            await ctx.send("You have not setup")
            return
        self.start_time = time.time()
        self.timer.start()
        await ctx.send('Starting the game!')

    @tasks.loop(seconds=10)
    async def timer(self):
        if self.start_time + self.game_length < time.time():
            self.timer.cancel()

        remaining_time = self.start_time + self.game_length - time.time()
        await self.text_channels["group-chat"].send((
            f"{str(int(remaining_time // 60)).zfill(2)}:{str(int(remaining_time % 60)).zfill(2)}"
        ))

    @commands.command()
    async def setup(self, ctx):
        # send character cards
        motives = list(range(1, 6))
        random.shuffle(motives)
        for i, character in enumerate(self.characters):
            channel = self.text_channels[f"{character.split()[0]}-clues"]
            asyncio.ensure_future(channel.send(file=discord.File(
                f"Images/Cards/Characters/{character.title()}.png"
            )))
            asyncio.ensure_future(channel.send(file=discord.File(
                f"Images/Cards/Motives/Motive {motives[i]}.png"
            )))
        self.setup = True
        await ctx.send("Done setting up")


def setup(bot):
    bot.add_cog(AliceIsMissing(bot))
