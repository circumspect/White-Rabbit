# Built-in
import asyncio
# 3rd-party
import discord
from discord.ext import commands
# Local
import gamedata
from localization import LOCALIZATION_DATA

loc = LOCALIZATION_DATA["commands"]["players"]

class Players(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Commands for players to claim character roles
    @commands.command(
        name=loc["claim"]["name"],
        aliases=loc["claim"]["aliases"],
        description=loc["claim"]["description"]
    )
    async def claim(self, ctx, role: discord.Role):
        """Claim a character/spectator role"""

        # Check if role can be claimed
        if role in ctx.author.roles:
            await ctx.send(loc["claim"]["AlreadyHaveThisRole"])
            return
        elif role.name.lower() not in [*gamedata.CHARACTERS, LOCALIZATION_DATA["spectator-role"]]:
            asyncio.create_task(ctx.send(loc["claim"]["UnclaimableRole"]))
            return
        elif role.members and role.name.lower() in gamedata.CHARACTERS:
            asyncio.create_task(ctx.send(loc["claim"]["RoleIsTaken"]))
            return

        # Check if player already has a character role
        for member_role in ctx.author.roles:
            if member_role.name.lower() in gamedata.CHARACTERS:
                asyncio.create_task(ctx.send(loc["claim"]["AlreadyHaveOtherRole"]))
                return

        # Give role and update player's nickname
        await ctx.author.add_roles(role)
        await ctx.send(loc["claim"]["UpdatedRoles"])
        if ctx.author == ctx.guild.owner:
            # Can't update nickname for server owner
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["ServerOwnerNicknameChange"]))
        elif role.name.lower() in gamedata.CHARACTERS:
            asyncio.create_task(ctx.author.edit(nick=gamedata.CHARACTERS[role.name.lower()]))

    @commands.command(
        name=loc["unclaim"]["name"],
        aliases=loc["unclaim"]["aliases"],
        description=loc["unclaim"]["description"]
    )
    async def unclaim(self, ctx):
        """Remove character roles"""

        # Keep @everyone
        for role in ctx.author.roles:
            if role.name.lower() in gamedata.CHARACTERS:
                await ctx.author.remove_roles(role)
                asyncio.create_task(ctx.send(f"Removed role {role.name}"))
                if ctx.author == ctx.guild.owner:
                    # Can't update nickname for server owner
                    asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["ServerOwnerNicknameChange"]))
                else:
                    asyncio.create_task(ctx.author.edit(nick=None))
                return
        await ctx.send(LOCALIZATION_DATA["errors"]["NoCharacterRoles"])

    @commands.command(
        name=loc["roles"]["name"],
        aliases=loc["roles"]["aliases"],
        description=loc["roles"]["description"]
    )
    async def roles(self, ctx):
        """Displays your roles"""

        message = loc["roles"]["YourRoles"] + "\n"
        message += f"{', '.join(role.name for role in ctx.author.roles[1:])}"
        await ctx.send(message)

    @commands.command(
        name=loc["users"]["name"],
        aliases=loc["users"]["aliases"],
        description=loc["users"]["description"]
    )
    async def users(self, ctx):
        """Lists all players and spectators"""

        message = ""
        if ctx.game.spectator_role.members:
            message += loc["users"]["spectators"]
            message += "\n"
            message += ', '.join(member.display_name for member in ctx.game.spectator_role.members)
            message += "\n"
        if ctx.game.char_roles():
            message += loc["users"]["players"]
            message += "\n"
            message += ', '.join(member.name for member in ctx.game.char_roles().values())
        await ctx.send(message if message else loc["users"]["NoneFound"])


def setup(bot):
    bot.add_cog(Players(bot))
