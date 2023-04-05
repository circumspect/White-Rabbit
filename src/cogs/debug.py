# Built-in
import asyncio
import logging
from os import environ
# 3rd-party
from discord.ext import commands
# Local
from data import gamedata
from data.wrappers import Bot, Context
from data.localization import LOCALIZATION_DATA
from envvars import get_env_var
import utils

loc = LOCALIZATION_DATA["commands"]["debug"]
DEBUG_COMMAND_LIST = (
    "speed",
    "plugins",
    "load",
    "unload",
    "quit",
)


class Debug(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        return get_env_var("WHITE_RABBIT_DEBUG")

    @commands.Cog.listener()
    async def on_ready(self):
        # Console logging
        logging.info("Bot has logged in!")

        if environ.get('WHITE_RABBIT_SHUTDOWN'):
            logging.info("Shutting down!")
            quit()

    @commands.command(
        name=loc["speed"]["name"],
        aliases=loc["speed"]["aliases"],
        description=loc["speed"]["description"]
    )
    async def speed(self, ctx: Context, speed: int = 1):
        """Changes the speed of the game - DEBUG USE ONLY"""

        ctx.game.game_speed = speed

        # Set timer to only ping once every minute to avoid
        # hitting discord api limits
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

    @commands.command(
        name=loc["plugins"]["name"],
        aliases=loc["plugins"]["aliases"],
        description=loc["plugins"]["description"]
    )
    async def plugins(self, ctx: Context):
        """Lists all currently loaded plugins"""

        message = "Plugins loaded:"
        message += "\n".join(self.bot.cogs.keys())
        message = utils.codeblock(message)
        await ctx.send(message)

    @commands.command(
        name=loc["load"]["name"],
        aliases=loc["load"]["aliases"],
        description=loc["load"]["description"]
    )
    async def load(self, ctx: Context, extension_name: str = "all"):
        """(Re)loads a plugin"""

        extension_name = extension_name.lower()

        # Reload all
        if extension_name == "all":
            # avoid RuntimeError: dictionary keys changed during iteration
            extensions = list(self.bot.extensions.keys())
            for extension in extensions:
                await self.bot.reload_extension(extension)
            asyncio.create_task(ctx.send(f"Reloaded {', '.join(self.bot.extensions.keys())}"))
            return

        # Load extension
        try:
            if extension_name in self.bot.extensions:
                await self.bot.reload_extension(extension_name)
            else:
                await self.bot.load_extension(extension_name)
            asyncio.create_task(ctx.send(f"Loaded {extension_name}"))

        except commands.errors.ExtensionNotFound:
            asyncio.create_task(ctx.send(f"Couldn't find plugin: \"{extension_name}\""))

    @commands.command(
        name=loc["unload"]["name"],
        aliases=loc["unload"]["aliases"],
        description=loc["unload"]["description"]
    )
    async def unload(self, ctx: Context, extension_name: str):
        """Unloads a plugin"""
        try:
            await self.bot.unload_extension(extension_name)
            asyncio.create_task(ctx.send(f"Unloaded {extension_name}"))
        except commands.errors.ExtensionNotLoaded:
            asyncio.create_task(ctx.send(f"{extension_name} was never loaded"))

    # DO NOT MOVE TO admin.py!!! This command will shut down the bot across
    # ALL servers, and thus should only be able to be run in debug mode
    @commands.command(
        name=loc["quit"]["name"],
        aliases=loc["quit"]["aliases"],
        description=loc["quit"]["description"]
    )
    async def quit(self, ctx: Context):
        """Shuts down the bot - AFFECTS ALL SERVERS"""

        await ctx.send("Shutting down, thanks for playing!")
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Debug(bot))
