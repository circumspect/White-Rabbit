# Built-in
import asyncio
# 3rd-party
from discord.ext import commands
# Local
from data import gamedata
from data.localization import LOCALIZATION_DATA
import utils

loc = LOCALIZATION_DATA["commands"]["settings"]


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name=loc["auto"]["name"],
        aliases=loc["auto"]["aliases"],
        description=loc["auto"]["description"]
    )
    async def auto(self, ctx: commands.Context, mode: str = ""):
        """
        Prints current mode or turn automatic on/off (on by default)

        Syntax:
        !auto will display the current mode
        !auto on will switch to automatic mode
        !auto off will switch to manual mode
        Automatic mode will disable manual card draw commands
        """

        if not mode:
            # Print current mode
            if ctx.game.automatic:
                message = loc["auto"]["CurrentlyAuto"]
            else:
                message = loc["auto"]["CurrentlyManual"]

            message = utils.codeblock(message)
            asyncio.create_task(ctx.send(message))
        elif mode == loc["auto"]["on"]:
            ctx.game.automatic = True
            asyncio.create_task(ctx.send(loc["auto"]["AutoEnabled"]))
        elif mode == loc["auto"]["off"]:
            ctx.game.automatic = False
            asyncio.create_task(ctx.send(loc["auto"]["AutoDisabled"]))
        else:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["UserInputError"]))

    @commands.command(
        hidden=True, name=loc["music"]["name"],
        aliases=loc["music"]["aliases"],
        description=loc["music"]["description"]
    )
    async def music(self, ctx: commands.Context):
        """Enable/disable music stream when game starts"""

        ctx.game.stream_music = not ctx.game.stream_music
        if ctx.game.stream_music:
            asyncio.create_task(ctx.send(loc["music"]["MusicEnabled"]))
        else:
            asyncio.create_task(ctx.send(loc["music"]["MusicDisabled"]))

    @commands.command(
        name=loc["show_timer"]["name"],
        aliases=loc["show_timer"]["aliases"],
        description=loc["show_timer"]["description"]
    )
    async def show_timer(self, ctx: commands.Context, gap: int = 0):
        """
        Show/hide bot timer

        Takes optional argument of how often to
        send timer messages (in seconds)
        """

        if gap:
            if gap < gamedata.MIN_TIMER_GAP:
                asyncio.create_task(ctx.send(
                    loc["show_timer"]["TimerGapTooSmall"]
                ))
                return

            # If timer spacing between pings exists, enable timer
            ctx.game.show_timer = True
            ctx.game.timer_gap = gap
        else:
            ctx.game.show_timer = not ctx.game.show_timer

        if ctx.game.show_timer:
            asyncio.create_task(ctx.send(loc["show_timer"]["ShowingTimer"]))
        else:
            asyncio.create_task(ctx.send(loc["show_timer"]["HidingTimer"]))

    @commands.command(
        hidden=True, name=loc["endings"]["name"],
        aliases=loc["endings"]["aliases"],
        description=loc["endings"]["description"]
    )
    async def endings(self, ctx: commands.Context, index: int = 0):
        """Enables/disables an ending. See docs for details"""

        if not index:
            # Print out currently enabled endings
            message = loc["endings"]["EndingsEnabled"] + "\n"
            message += ", ".join(
                f"{end}" for end in ctx.game.endings if ctx.game.endings[end]
            )

            message = utils.codeblock(message)
            asyncio.create_task(ctx.send(message))
        else:
            # Toggle specified ending
            ctx.game.endings[index] = not ctx.game.endings[index]


async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot))
