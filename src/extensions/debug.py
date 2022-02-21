from os import environ
import asyncio

import lightbulb
from lightbulb import commands

from utils.localization import LOCALIZATION_DATA
from utils import constants, filepaths, gamedata, miscutils

plugin = lightbulb.Plugin("Debug")
loc = LOCALIZATION_DATA["commands"]["debug"]


DEBUG_COMMAND_LIST = (
    "speed",
    "plugins",
    "load",
    "unload",
    "quit",
)
async def cog_check(self, ctx):
    """Only people with access to the code"""

    return ctx.author.id in self.bot.d.dev_ids

@plugin.command()
@lightbulb.command(loc["load"]["name"], loc["load"]["description"], aliases=loc["load"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def load(ctx: lightbulb.Context) -> None:
    ctx.app.reload_extensions(*ctx.app.extensions)
    await ctx.respond("Reloaded")


@plugin.command()
@lightbulb.option("speed", "changes game run speed")
@lightbulb.command(loc["speed"]["name"], loc["speed"]["description"], aliases=loc["speed"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def speed(ctx: lightbulb.Context) -> None:
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


@plugin.command()
@lightbulb.command(loc["plugins"]["name"], loc["plugins"]["description"], aliases=loc["plugins"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def plugins(ctx: lightbulb.Context) -> None:
    """Lists all currently loaded plugins"""

    message = "Plugins loaded:"
    message += "\n".join(ctx.bot.cogs.keys())
    message = miscutils.codeblock(message)
    await ctx.send(message)


@plugin.command()
@lightbulb.command(loc["unload"]["name"], loc["unload"]["description"], aliases=loc["unload"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def unload(ctx: lightbulb.Context) -> None:
    """Unloads a plugin"""
    extension_name = ""
    try:
        ctx.bot.unload_extension(extension_name)
        asyncio.create_task(ctx.send(f"Unloaded {extension_name}"))
    except commands.errors.ExtensionNotLoaded:
        asyncio.create_task(ctx.send(f"{extension_name} was never loaded"))

# DO NOT MOVE TO admin.py!!! This command will shut down the bot across
# ALL servers, and thus should only be able to be run by those listed
# in the dev_ids file

@plugin.command()
@lightbulb.command(loc["quit"]["name"], loc["quit"]["description"], aliases=loc["quit"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def quit(ctx: lightbulb.Context) -> None:
    """Shuts down the bot - AFFECTS ALL SERVERS"""

    await ctx.send("Shutting down, thanks for playing!")
    await ctx.bot.close()


def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)