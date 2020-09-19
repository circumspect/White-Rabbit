# Built-in
import asyncio
# 3rd-party
import discord
from discord.ext import commands
# Local
import game

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

        if role.name.lower() not in game.CHARACTERS:
            await ctx.send("You cannot claim that role")
        elif len(ctx.author.roles) > 1:
            await ctx.send(f"You already have {ctx.author.roles[-1].name}")
        elif role.members:
            await ctx.send("That role is taken")
        else:
            await ctx.author.add_roles(role)
            await ctx.send(f"Gave you {role.name}!")

    @commands.command()
    async def unclaim(self, ctx):
        """Remove all assigned roles"""
        
        # Keep @everyone
        await ctx.author.edit(roles=[ctx.author.roles[0]])
        await ctx.send("Cleared your roles!")


def setup(bot):
    bot.add_cog(Players(bot))
