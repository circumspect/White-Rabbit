import asyncio

import lightbulb
from lightbulb import commands
from utils.localization import LOCALIZATION_DATA
from utils import gamedata, miscutils

loc = LOCALIZATION_DATA["commands"]["settings"]


plugin = lightbulb.Plugin("Settings")

@plugin.command()
@lightbulb.command(loc["auto"]["name"], loc["auto"]["description"], aliases=loc["auto"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def auto(ctx: lightbulb.Context) -> None:
    """
    Prints current mode or turn automatic on/off (on by default)

    Syntax:
    !auto will display the current mode
    !auto on will switch to automatic mode
    !auto off will switch to manual mode
    Automatic mode will disable manual card draw commands
    """
    mode = ""
    if not mode:
        # Print current mode
        if ctx.game.automatic:
            message = loc["auto"]["CurrentlyAuto"]
        else:
            message = loc["auto"]["CurrentlyManual"]

        message = miscutils.codeblock(message)
        asyncio.create_task(ctx.respond(message))
    elif mode == loc["auto"]["on"]:
        ctx.game.automatic = True
        asyncio.create_task(ctx.respond(loc["auto"]["AutoEnabled"]))
    elif mode == loc["auto"]["off"]:
        ctx.game.automatic = False
        asyncio.create_task(ctx.respond(loc["auto"]["AutoDisabled"]))
    else:
        asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["UserInputError"]))


@plugin.command()
@lightbulb.command(loc["music"]["name"], loc["music"]["description"], aliases=loc["music"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def music(ctx: lightbulb.Context) -> None:
    """Enable/disable music stream when game starts"""

    ctx.game.stream_music = not ctx.game.stream_music
    if ctx.game.stream_music:
        asyncio.create_task(ctx.respond(loc["music"]["MusicEnabled"]))
    else:
        asyncio.create_task(ctx.respond(loc["music"]["MusicDisabled"]))

@plugin.command()
@lightbulb.command(loc["show_timer"]["name"], loc["show_timer"]["description"], aliases=loc["show_timer"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def show_timer(ctx: lightbulb.Context) -> None:
    """
    Show/hide bot timer

    Takes optional argument of how often to
    send timer messages (in seconds)
    """
    gap = 0

    if gap:
        if gap < gamedata.MIN_TIMER_GAP:
            asyncio.create_task(ctx.respond(
                loc["show_timer"]["TimerGapTooSmall"]
            ))
            return

        # If timer spacing between pings exists, enable timer
        ctx.game.show_timer = True
        ctx.game.timer_gap = gap
    else:
        ctx.game.show_timer = not ctx.game.show_timer

    if ctx.game.show_timer:
        asyncio.create_task(ctx.respond(loc["show_timer"]["ShowingTimer"]))
    else:
        asyncio.create_task(ctx.respond(loc["show_timer"]["HidingTimer"]))

@plugin.command()
@lightbulb.command(loc["endings"]["name"], loc["endings"]["description"], aliases=loc["endings"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def endings(ctx: lightbulb.Context) -> None:
    """Enables/disables an ending. See docs for details"""
    index = 0
    if not index:
        # Print out currently enabled endings
        message = loc["endings"]["EndingsEnabled"] + "\n"
        message += ", ".join(
            f"{end}" for end in ctx.game.endings if ctx.game.endings[end]
        )

        message = miscutils.codeblock(message)
        asyncio.create_task(ctx.respond(message))
    else:
        # Toggle specified ending
        ctx.game.endings[index] = not ctx.game.endings[index]


def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
