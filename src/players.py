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

    # Commands for players to claim character roles
    @commands.command()
    async def claim(self, ctx, role: discord.Role):
        """Claim a character/spectator role"""

        # Check if role can be claimed
        if role in ctx.author.roles:
            await ctx.send("You already have that role")
            return
        elif role.name.lower() not in [*gamedata.CHARACTERS, "spectator"]:
            asyncio.create_task(ctx.send("You cannot claim that role"))
            return
        elif role.members and role.name.lower() in gamedata.CHARACTERS:
            asyncio.create_task(ctx.send(f"That role is taken by {role.members[0].name}"))
            return

        # Check if player already has a character role
        for member_role in ctx.author.roles:
            if member_role.name.lower() in gamedata.CHARACTERS:
                asyncio.create_task(ctx.send(f"You already have {member_role.name}"))
                return

        # Give role and update player's nickname
        await ctx.author.add_roles(role)
        await ctx.send(f"Gave you {role.name}!")
        if ctx.author == ctx.guild.owner:
            # Can't update nickname for server owner
            asyncio.create_task(ctx.send("Couldn't update nickname because you are server owner!"))
        elif role.name.lower() in gamedata.CHARACTERS:
            asyncio.create_task(ctx.author.edit(nick=gamedata.CHARACTERS[role.name.lower()]))

    @commands.command()
    async def unclaim(self, ctx):
        """Remove character roles"""

        # Keep @everyone
        for role in ctx.author.roles:
            if role.name.lower() in gamedata.CHARACTERS:
                await ctx.author.remove_roles(role)
                asyncio.create_task(ctx.send(f"Removed role {role.name}"))
                if ctx.author == ctx.guild.owner:
                    # Can't update nickname for server owner
                    asyncio.create_task(ctx.send("Couldn't update nickname because you are server owner!"))
                else:
                    asyncio.create_task(ctx.author.edit(nick=None))
                return
        await ctx.send("You don't have any character roles!")

    @commands.command()
    async def roles(self, ctx):
        """Displays your roles"""

        await ctx.send(f"Your roles: {', '.join(role.name for role in ctx.author.roles[1:len(ctx.author.roles)])}")
    
    @commands.command(name="list")
    async def users(self, ctx):
        """Lists all players and spectators"""

        await ctx.send(f"")


def setup(bot):
    bot.add_cog(Players(bot))
