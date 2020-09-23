# Built-in
import asyncio
# 3rd-party
import discord
from discord.ext import commands, tasks
# Local
import gamedata

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
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
            message = "```\nCurrent mode: "
            if ctx.game.automatic:
                message += "automatic"
            else:
                message += "manual"
            message += "\n```"
            await ctx.send(message)
        elif mode == "on":
            ctx.game.automatic = True
            await ctx.send("Automatic card draw enabled!")
        elif mode == "off":
            ctx.game.automatic = False
            await ctx.send("Automatic card draw disabled!")
        else:
            await ctx.send("Input error, try !auto on or !auto off")

    @commands.command()
    async def music(self, ctx):
        """Enable/disable music stream when game starts"""

        ctx.game.stream_music = not ctx.game.stream_music
        if ctx.game.stream_music:
            await ctx.send("Music stream enabled!")
        else:
            await ctx.send("Music stream disabled!")

    @commands.command(name="timer")
    async def show_timer(self, ctx, gap: int=0):
        """
        Show/hide bot timer
        
        Takes optional argument of how often to 
        send timer messages (in seconds)
        """

        if gap:
            if gap < gamedata.MIN_TIMER_GAP:
                asyncio.create_task(
                    ctx.send("Can't set timer pings less than "
                                + str(gamedata.MIN_TIMER_GAP)
                                + " seconds apart!")
                )
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

def setup(bot):
    bot.add_cog(Settings(bot))