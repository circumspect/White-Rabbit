import discord
import time
from discord.ext import commands


class AliceIsMissing(commands.Cog):
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
