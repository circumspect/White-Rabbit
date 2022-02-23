from os import environ

import hikari
import lightbulb

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

    if environ.get("SHUTDOWN"):
        print("Shutting down!")
        await quit(event.context)


@plugin.command()
@lightbulb.option("speed", "speed to run the game at", type=float)
@lightbulb.command(
    loc["speed"]["name"], loc["speed"]["description"], aliases=loc["speed"]["aliases"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def speed(ctx: lightbulb.Context) -> None:
    """Changes the speed of the game - DEBUG USE ONLY"""

    # Cap the top speed
    if ctx.options.speed > gamedata.MAX_SPEED:
        await ctx.respond(f"Too fast! Max is {gamedata.MAX_SPEED}")
        return
    # Speed must be at least 1
    elif ctx.options.speed < 1:
        await ctx.respond("Too slow! Speed must be at least 1")
        return

    game = ctx.bot.d.games[ctx.guild_id]
    game.game_speed = ctx.options.speed

    # Set timer to only ping once every minute to avoid
    # hitting discord api limits
    game.timer_gap = 60

    if ctx.options.speed == 1:
        await ctx.respond("Reset the game speed!")
    else:
        await ctx.respond("Set the game speed!")


@plugin.command()
@lightbulb.command(
    loc["plugins"]["name"],
    loc["plugins"]["description"],
    aliases=loc["plugins"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def plugins(ctx: lightbulb.Context) -> None:
    """Lists all currently loaded plugins"""

    message = "Plugins loaded:\n"
    message += "\n".join(ctx.bot.extensions)
    message = miscutils.codeblock(message)
    await ctx.respond(message)


@plugin.command()
@lightbulb.option("extension", "name of the extension to load", type=str, default="all")
@lightbulb.command(
    loc["load"]["name"], loc["load"]["description"], aliases=loc["load"]["aliases"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def load(ctx: lightbulb.Context) -> None:
    extension_name = ctx.options.extension.lower()

    # Reload all
    if ctx.options.extension.lower() == "all":
        ctx.bot.reload_extensions(*ctx.bot.extensions)
        await ctx.respond(f"Reloaded {', '.join(ctx.bot.extensions)}")
    # Load extension
    else:
        try:
            for extension in ctx.bot.extensions:
                if (
                    extension_name == extension.split(".")[-1]
                    or extension_name == extension
                ):
                    ctx.bot.reload_extensions(extension)
                    break
            else:
                ctx.bot.load_extensions(extension_name)
            await ctx.respond(f"Loaded {extension_name}")

        except lightbulb.ExtensionNotFound:
            await ctx.respond(
                f"Couldn't find extension: {extension_name}, did you mean extensions.{extension_name}?"
            )


@plugin.command()
@lightbulb.option("extension", "name of the extension to unload", type=str)
@lightbulb.command(
    loc["unload"]["name"],
    loc["unload"]["description"],
    aliases=loc["unload"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def unload(ctx: lightbulb.Context) -> None:
    """Unloads a plugin"""
    extension_name = ctx.options.extension
    try:
        for extension in ctx.bot.extensions:
            if (
                extension_name == extension.split(".")[-1]
                or extension_name == extension
            ):
                ctx.bot.unload_extensions(extension)
                break
        await ctx.respond(f"Unloaded {ctx.options.extension}")
    except lightbulb.errors.ExtensionNotLoaded:
        await ctx.respond(f"{ctx.options.extension} was never loaded")


# DO NOT MOVE TO admin.py!
# This command will shut down the bot across ALL servers,
# and thus should only be able to be run by those listed in the dev_ids file
@plugin.command()
@lightbulb.command(
    loc["quit"]["name"], loc["quit"]["description"], aliases=loc["quit"]["aliases"]
)
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
