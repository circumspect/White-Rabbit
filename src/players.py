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
        """Claim a character role"""
        # check role can be claimed
        if role in ctx.author.roles:
            await ctx.send("You already have that role")
            return
        elif role.name.lower() not in gamedata.CHARACTERS:
            asyncio.create_task(ctx.send("You cannot claim that role"))
            return
        elif role.members:
            asyncio.create_task(ctx.send(
                f"That role is taken by {role.members[0].name}"
            ))
            return

        # cannot have multiple characters
        for member_role in ctx.author.roles:
            if member_role.name.lower() in gamedata.CHARACTERS:
                asyncio.create_task(ctx.send(
                    f"You already have {member_role.name}"
                ))
                return

        asyncio.create_task(ctx.author.add_roles(role))
        asyncio.create_task(ctx.author.edit(
            nick=gamedata.CHARACTERS[role.name.lower()]
        ))
        asyncio.create_task(ctx.send(f"Gave you {role.name}!"))

    @commands.command()
    async def unclaim(self, ctx):
        """Remove character roles"""
        # Keep @everyone
        for role in ctx.author.roles:
            if role.name.lower() in gamedata.CHARACTERS:
                await ctx.author.remove_roles(role)
                try:
                    asyncio.create_task(ctx.author.edit(nick=None))
                except discord.errors.Forbidden:
                    ctx.send("could not change nickname")
                asyncio.create_task(ctx.send(f"Removed role {role.name}"))
                return
        await ctx.send("You don't have any character roles")

    @commands.command()
    async def roles(self, ctx):
        """Get list of roles"""
        await ctx.send(
            f"You have {', '.join(role.name for role in ctx.author.roles)}"
        )


def setup(bot):
    bot.add_cog(Players(bot))
