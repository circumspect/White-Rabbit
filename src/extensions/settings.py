import asyncio

import lightbulb
from utils.localization import LOCALIZATION_DATA
from utils import gamedata, miscutils, errors

loc = LOCALIZATION_DATA["commands"]["settings"]


plugin = lightbulb.Plugin("Settings")


@plugin.command()
@lightbulb.option("mode", "what to set auto to (on/off)", type=str, default="")
@lightbulb.command(
    loc["auto"]["name"], loc["auto"]["description"], aliases=loc["auto"]["aliases"]
)
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
    game = ctx.bot.d.games[ctx.guild_id]
    if not ctx.options.mode:
        # Print current mode
        if game.automatic:
            message = loc["auto"]["CurrentlyAuto"]
        else:
            message = loc["auto"]["CurrentlyManual"]
        message = miscutils.codeblock(message)
        await ctx.respond(message)

    elif ctx.options.mode == loc["auto"]["on"]:
        game.automatic = True
        await ctx.respond(loc["auto"]["AutoEnabled"])

    elif ctx.options.mode == loc["auto"]["off"]:
        game.automatic = False
        await ctx.respond(loc["auto"]["AutoDisabled"])

    else:
        raise errors.BadInput()


@plugin.command()
@lightbulb.command(
    loc["music"]["name"], loc["music"]["description"], aliases=loc["music"]["aliases"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def music(ctx: lightbulb.Context) -> None:
    """Enable/disable music stream when game starts"""
    await ctx.respond("Music streaming is currently broken")
    return
    game = ctx.bot.d.games[ctx.guild_id]
    game.stream_music = not game.stream_music
    if game.stream_music:
        await ctx.respond(loc["music"]["MusicEnabled"])
    else:
        await ctx.respond(loc["music"]["MusicDisabled"])


@plugin.command()
@lightbulb.option("gap", "gap between timer messages", type=int, default=0)
@lightbulb.command(
    loc["show_timer"]["name"],
    loc["show_timer"]["description"],
    aliases=loc["show_timer"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def show_timer(ctx: lightbulb.Context) -> None:
    """
    Show/hide bot timer

    Takes optional argument of how often to
    send timer messages (in seconds)
    """
    game = ctx.bot.d.games[ctx.guild_id]
    if ctx.options.gap:
        if ctx.options.gap < gamedata.MIN_TIMER_GAP:
            asyncio.create_task(ctx.respond(loc["show_timer"]["TimerGapTooSmall"]))
            return

        # If timer spacing between pings exists, enable timer
        game.show_timer = True
        game.timer_gap = ctx.options.gap
    else:
        game.show_timer = not game.show_timer

    if game.show_timer:
        asyncio.create_task(ctx.respond(loc["show_timer"]["ShowingTimer"]))
    else:
        asyncio.create_task(ctx.respond(loc["show_timer"]["HidingTimer"]))


@plugin.command()
@lightbulb.option("index", "index of ending to toggle", type=int, default=0)
@lightbulb.command(
    loc["endings"]["name"],
    loc["endings"]["description"],
    aliases=loc["endings"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def endings(ctx: lightbulb.Context) -> None:
    """Enables/disables an ending. See docs for details"""
    game = ctx.bot.d.games[ctx.guild_id]
    if not ctx.options.index:
        # Print out currently enabled endings
        message = loc["endings"]["EndingsEnabled"] + "\n"
        message += ", ".join(f"{end}" for end in game.endings if game.endings[end])

        message = miscutils.codeblock(message)
        asyncio.create_task(ctx.respond(message))
    else:
        # Toggle specified ending
        game.endings[ctx.options.index] = not game.endings[ctx.options.index]


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
