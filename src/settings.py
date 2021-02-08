# Built-in
import asyncio
# 3rd-party
import discord
from discord.ext import commands, tasks
# Local
import gamedata
from localization import LOCALIZATION_DATA
import utils

loc = LOCALIZATION_DATA["commands"]["settings"]

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name=loc["auto"]["name"], aliases=loc["auto"]["aliases"], description=loc["auto"]["description"])
    async def auto(self, ctx, mode: str=""):
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
            message = "Current mode: "
            if ctx.game.automatic:
                message += "automatic"
            else:
                message += "manual"
            
            message = utils.codeblock(message)
            await ctx.send(message)
        elif mode == "on":
            ctx.game.automatic = True
            await ctx.send("Automatic card draw enabled!")
        elif mode == "off":
            ctx.game.automatic = False
            await ctx.send("Automatic card draw disabled!")
        else:
            await ctx.send("Input error, try !auto on or !auto off")

    @commands.command(hidden=True, name=loc["music"]["name"], aliases=loc["music"]["aliases"], description=loc["music"]["description"])
    async def music(self, ctx):
        """Enable/disable music stream when game starts"""

        ctx.game.stream_music = not ctx.game.stream_music
        if ctx.game.stream_music:
            await ctx.send("Music stream enabled!")
        else:
            await ctx.send("Music stream disabled!")

    @commands.command(name=loc["show_timer"]["name"], aliases=loc["show_timer"]["aliases"], description=loc["show_timer"]["description"])
    async def show_timer(self, ctx, gap: int = 0):
        """
        Show/hide bot timer
        
        Takes optional argument of how often to 
        send timer messages (in seconds)
        """

        if gap:
            if gap < gamedata.MIN_TIMER_GAP:
                asyncio.create_task(ctx.send(
                    f"Can't set timer pings less than {gamedata.MIN_TIMER_GAP} seconds apart!"
                ))
                return
                
            # If timer spacing between pings exists, enable timer
            ctx.game.show_timer = True
            ctx.game.timer_gap = gap
        else:
            ctx.game.show_timer = not ctx.game.show_timer

        if ctx.game.show_timer:
            await ctx.send("Showing bot timer!")
        else:
            await ctx.send("Hiding bot timer!")

    @commands.command(hidden=True, name=loc["endings"]["name"], aliases=loc["endings"]["aliases"], description=loc["endings"]["description"])
    async def endings(self, ctx, index: int=0):
        """Enables/disables an ending. See docs for details"""

        if not index:
            # Print out currently enabled endings
            message = "Endings enabled: "
            message += ", ".join([f"#{end}" for end in ctx.game.endings if ctx.game.endings[end]])
            message = utils.codeblock(message)
            await ctx.send(message)
        else:
            # Toggle specified ending
            ctx.game.endings[index] = not ctx.game.endings[index]

def setup(bot):
    bot.add_cog(Settings(bot))
