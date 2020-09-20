# Built-in
import asyncio
# 3rd-party
import discord
from discord.ext import commands
# Local
import gamedata

class Players(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    # Commands for players to claim character roles
    @commands.command()
    async def claim(self, ctx, role: discord.Role):
        """Claim a character role"""

        if role.name.lower() not in gamedata.CHARACTERS:
            asyncio.create_task(ctx.send("You cannot claim that role"))
        elif len(ctx.author.roles) > 1:
            asyncio.create_task(ctx.send(f"You already have {ctx.author.roles[-1].name}"))
        elif role.members:
            asyncio.create_task(ctx.send("That role is taken"))
        else:
            ctx.game.char_roles[role.name] = role
            asyncio.create_task(ctx.author.add_roles(role))
            asyncio.create_task(ctx.author.edit(nick=gamedata.CHARACTERS[role.name.lower()]))
            asyncio.create_task(ctx.send(f"Gave you {role.name}!"))

    @commands.command()
    async def unclaim(self, ctx):
        """Remove all assigned roles"""
        
        # Keep @everyone
        thisdict.pop(ctx.author.roles[-1].name)
        asyncio.create_task(ctx.author.edit(roles=[ctx.author.roles[0]]))
        asyncio.create_task(ctx.author.edit(nick=None))
        asyncio.create_task(ctx.send("Cleared your roles!"))


def setup(bot):
    bot.add_cog(Players(bot))
