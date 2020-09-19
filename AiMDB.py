import discord
import time
import random
import asyncio
from discord.ext import commands


class AliceIsMissing(commands.Cog):
    characters = ("charlie barnes", "dakota travis", "evan holwell", "jack briarwood", "julia north")

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot has logged in as {self.bot}")

    @commands.command()
    async def start(self, ctx):
        start_time = time.time()
        await ctx.send('Starting the game!')

    @commands.command()
    async def setup(self, ctx):
        self.text_channels = {channel.name: channel for channel in ctx.guild.text_channels}

        # send character cards
        motives = list(range(1, 6))
        random.shuffle(motives)
        for i, character in enumerate(self.characters):
            channel = self.text_channels[f"{character.split()[0]}-clues"]
            asyncio.ensure_future(channel.send(file=discord.File(f"Images/Cards/Characters/{character.title()}.png")))
            asyncio.ensure_future(channel.send(file=discord.File(f"Images/Cards/Motives/Motive {motives[i]}.png")))
