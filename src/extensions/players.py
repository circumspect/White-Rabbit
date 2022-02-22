# Built-in
import asyncio

import lightbulb
from lightbulb import commands

from utils import constants, gamedata
from utils.localization import LOCALIZATION_DATA

loc = LOCALIZATION_DATA["commands"]["players"]
plugin = lightbulb.Plugin("Players")


# Commands for players to claim character roles
@plugin.command()
@lightbulb.command(loc["claim"]["name"], loc["claim"]["description"], aliases=loc["claim"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def claim(ctx: lightbulb.Context) -> None:
    """Claim a character/spectator role"""

    # Check if role can be claimed
    role = None
    if role in ctx.author.roles:
        await ctx.respond(loc["claim"]["AlreadyHaveThisRole"])
        return
    elif role.name.lower() not in [*gamedata.CHARACTERS, LOCALIZATION_DATA["spectator-role"]]:
        asyncio.create_task(ctx.respond(loc["claim"]["UnclaimableRole"]))
        return
    elif role.members and role.name.lower() in gamedata.CHARACTERS:
        asyncio.create_task(ctx.respond(loc["claim"]["RoleIsTaken"]))
        return

    # Check if player already has a character role
    for member_role in ctx.author.roles:
        if member_role.name.lower() in gamedata.CHARACTERS:
            asyncio.create_task(ctx.respond(loc["claim"]["AlreadyHaveOtherRole"]))
            return

    # Give role and update player's nickname
    await ctx.author.add_roles(role)
    await ctx.respond(loc["claim"]["UpdatedRoles"])
    if ctx.author == ctx.guild.owner:
        # Can't update nickname for server owner
        asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["ServerOwnerNicknameChange"]))
    elif role.name.lower() in gamedata.CHARACTERS:
        asyncio.create_task(
            ctx.author.edit(nick=gamedata.CHARACTERS[role.name.lower()])
        )


@plugin.command()
@lightbulb.command(loc["unclaim"]["name"], loc["unclaim"]["description"], aliases=loc["unclaim"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def unclaim(ctx: lightbulb.Context) -> None:
    """Remove character roles"""

    # Keep @everyone
    for role in ctx.author.roles:
        if role.name.lower() in gamedata.CHARACTERS:
            await ctx.author.remove_roles(role)
            asyncio.create_task(ctx.respond(f"Removed role {role.name}"))
            if ctx.author == ctx.guild.owner:
                # Can't update nickname for server owner
                asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["ServerOwnerNicknameChange"]))
            else:
                asyncio.create_task(ctx.author.edit(nick=None))
            return
    await ctx.respond(LOCALIZATION_DATA["errors"]["NoCharacterRoles"])

@plugin.command()
@lightbulb.command(loc["roles"]["name"], loc["roles"]["description"], aliases=loc["roles"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def roles(ctx: lightbulb.Context) -> None:
    """Displays your roles"""

    message = loc["roles"]["YourRoles"] + "\n"
    message += f"{', '.join(role.name for role in ctx.author.roles[1:])}"
    await ctx.respond(message)

@plugin.command()
@lightbulb.command(loc["users"]["name"], loc["users"]["description"], aliases=loc["users"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def users(ctx: lightbulb.Context) -> None:
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
    await ctx.respond(message or loc["users"]["NoneFound"])

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
