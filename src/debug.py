# Built-in
import asyncio
# 3rd-party
import discord
from discord.ext import commands
# Local
import gamedata
import utils
from localization import LOCALIZATION_DATA

loc = LOCALIZATION_DATA["commands"]["debug"]

class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        try:
            with open(utils.DEV_ID_FILE) as f:
                self.dev_ids = [int(line.strip()) for line in f.readlines()]
        except FileNotFoundError:
            # Create file if it doesn't exist
            print("No " + utils.DEV_ID_FILE.name + " found, making empty file")
            with open(utils.DEV_ID_FILE, 'x') as f:
                pass

    async def cog_check(self, ctx):
        """Only people with access to the code"""
        return ctx.author.id in self.dev_ids

    @commands.Cog.listener()
    async def on_ready(self):
        # Console logging
        print("Bot has logged in!")

    @commands.command(aliases=loc["speed"]["aliases"], description=loc["speed"]["description"])
    async def speed(self, ctx, speed: float=1):
        """Changes the speed of the game - DEBUG USE ONLY"""

        ctx.game.game_speed = speed

        # Set timer to only ping once every minute to avoid hitting discord api limits
        ctx.game.timer_gap = 60

        # Cap the top speed
        if speed > gamedata.MAX_SPEED:
            asyncio.create_task(ctx.send(f"Too fast! Max is {gamedata.MAX_SPEED}"))
            return
        
        # Speed must be at least 1
        if speed < 1:
            asyncio.create_task(ctx.send("Too slow! Speed must be at least 1"))
            return

        if speed == 1:
            asyncio.create_task(ctx.send("Reset the game speed!"))
        else:
            asyncio.create_task(ctx.send("Set the game speed!"))

    @commands.command(aliases=loc["plugins"]["aliases"], description=loc["plugins"]["description"])
    async def plugins(self, ctx):
        """Lists all currently loaded plugins"""

        message = "Plugins loaded:"
        message += "\n".join(self.bot.cogs.keys())
        message = utils.codeblock(message)
        await ctx.send(message)

    @commands.command(aliases=loc["load"]["aliases"], description=loc["load"]["description"])
    async def load(self, ctx, extension_name: str = "all"):
        """(Re)loads a plugin"""

        extension_name = extension_name.lower()

        # Reload all
        if extension_name == "all":
            # avoid RuntimeError: dictionary keys changed during iteration
            extensions = list(self.bot.extensions.keys())
            for extension in extensions:
                self.bot.reload_extension(extension)
            await ctx.send(f"Reloaded {', '.join(self.bot.extensions.keys())}")
            return

        # Load extension
        try:
            if extension_name in self.bot.extensions:
                self.bot.reload_extension(extension_name)
            else:
                self.bot.load_extension(extension_name)
            await ctx.send(f"Loaded {extension_name}")

        except commands.errors.ExtensionNotFound:
            await ctx.send(f"Couldn't find plugin: \"{extension_name}\"")

    @commands.command(aliases=loc["unload"]["aliases"], description=loc["unload"]["description"])
    async def unload(self, ctx, extension_name: str):
        """Unloads a plugin"""
        try:
            self.bot.unload_extension(extension_name)
            await ctx.send(f"Unloaded {extension_name}")
        except commands.errors.ExtensionNotLoaded:
            await ctx.send(f"{extension_name} was never loaded")

    # DO NOT MOVE TO admin.py!!! This command will shut down the bot across 
    # ALL servers, and thus should only be able to be run by those listed
    # in the dev_ids file
    @commands.command(aliases=loc["quit"]["aliases"], description=loc["quit"]["description"])
    async def quit(self, ctx):
        """Shuts down the bot - AFFECTS ALL SERVERS"""

        await ctx.send("Shutting down, thanks for playing!")
        await self.bot.close()


def setup(bot):
    bot.add_cog(Debug(bot))
