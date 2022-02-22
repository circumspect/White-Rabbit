from os import environ
import asyncio

import hikari
import lightbulb
from lightbulb import commands

from utils.localization import LOCALIZATION_DATA
from utils import gamedata, miscutils, errors

plugin = lightbulb.Plugin("Debug")
loc = LOCALIZATION_DATA["commands"]["debug"]

@lightbulb.Check
def is_dev(ctx: lightbulb.Context):
    """Only people with access to the code"""
    if not ctx.author.id in ctx.bot.d.dev_ids:
        raise errors.DevOnly()
    return True

plugin.add_checks(is_dev)

async def on_ready(event: hikari.StartedEvent):
    # Console logging
    print("Bot has logged in!")

    if environ.get('SHUTDOWN'):
        print("Shutting down!")
        quit()

@plugin.command()
@lightbulb.option("speed", "changes game run speed", type=float)
@lightbulb.command(loc["speed"]["name"], loc["speed"]["description"], aliases=loc["speed"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def speed(ctx: lightbulb.Context) -> None:
    """Changes the speed of the game - DEBUG USE ONLY"""

    # Cap the top speed
    if ctx.options.speed > gamedata.MAX_SPEED:
        asyncio.create_task(ctx.respond(f"Too fast! Max is {gamedata.MAX_SPEED}"))
        return
    # Speed must be at least 1
    elif ctx.options.speed < 1:
        asyncio.create_task(ctx.respond("Too slow! Speed must be at least 1"))
        return

    game = ctx.bot.d.games[ctx.guild_id]
    game.game_speed = ctx.options.speed

    # Set timer to only ping once every minute to avoid
    # hitting discord api limits
    game.timer_gap = 60

    if ctx.options.speed == 1:
        asyncio.create_task(ctx.respond("Reset the game speed!"))
    else:
        asyncio.create_task(ctx.respond("Set the game speed!"))


@plugin.command()
@lightbulb.command(loc["plugins"]["name"], loc["plugins"]["description"], aliases=loc["plugins"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def plugins(ctx: lightbulb.Context) -> None:
    """Lists all currently loaded plugins"""

    message = "Plugins loaded:\n"
    message += "\n".join(ctx.bot.extensions)
    message = miscutils.codeblock(message)
    await ctx.respond(message)


@plugin.command()
@lightbulb.command(loc["load"]["name"], loc["load"]["description"], aliases=loc["load"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def load(ctx: lightbulb.Context) -> None:
    ctx.bot.reload_extensions(*ctx.bot.extensions)
    await ctx.respond("Reloaded")


@plugin.command()
@lightbulb.command(loc["unload"]["name"], loc["unload"]["description"], aliases=loc["unload"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def unload(ctx: lightbulb.Context) -> None:
    """Unloads a plugin"""
    extension_name = ""
    try:
        ctx.bot.unload_extension(extension_name)
        asyncio.create_task(ctx.respond(f"Unloaded {extension_name}"))
    except commands.errors.ExtensionNotLoaded:
        asyncio.create_task(ctx.respond(f"{extension_name} was never loaded"))

# DO NOT MOVE TO admin.py!!! This command will shut down the bot across
# ALL servers, and thus should only be able to be run by those listed
# in the dev_ids file

@plugin.command()
@lightbulb.command(loc["quit"]["name"], loc["quit"]["description"], aliases=loc["quit"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def quit(ctx: lightbulb.Context) -> None:
    """Shuts down the bot - AFFECTS ALL SERVERS"""

    await ctx.respond("Shutting down, thanks for playing!")
    await ctx.bot.close()


def load(bot):
    bot.add_plugin(plugin)
    bot.subscribe(hikari.StartedEvent, on_ready)

def unload(bot):
    bot.remove_plugin(plugin)
    bot.unsubscribe(hikari.StartedEvent, on_ready)