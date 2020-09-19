# Built-in
import asyncio
# 3rd-party
import discord
from discord.ext import commands

class Players(commands.Cog):
    CHARACTERS = (
        "Charlie Barnes", "Dakota Travis", "Evan Holwell",
            "Jack Briarwood", "Julia North"
    )

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    # Commands for players to claim character roles
    @commands.command()
    async def claim(self, ctx, role: discord.Role):
        """Claim a character role"""
        if role.name.title() not in [name.split()[0] for name in self.CHARACTERS]:
            await ctx.send("You cannot claim that role")
        elif role.members:
            await ctx.send("That role is taken")
        elif len(ctx.author.roles) > 1:
            await ctx.send(f"You already have {ctx.author.roles[-1].name}")
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
