# Built-in
import asyncio

import hikari
import lightbulb

from utils import constants, gamedata
from utils.localization import LOCALIZATION_DATA

loc = LOCALIZATION_DATA["commands"]["players"]
plugin = lightbulb.Plugin("Players")


# Commands for players to claim character roles
@plugin.command()
@lightbulb.option("role", "role to claim", type=hikari.Role)
@lightbulb.command(
    loc["claim"]["name"], loc["claim"]["description"], aliases=loc["claim"]["aliases"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def claim(ctx: lightbulb.Context) -> None:
    """Claim a character/spectator role"""
    # Check if role can be claimed
    if ctx.options.role.id in ctx.member.role_ids:
        await ctx.respond(loc["claim"]["AlreadyHaveThisRole"])
        return
    elif ctx.options.role.name.lower() not in [
        *gamedata.CHARACTERS,
        LOCALIZATION_DATA["spectator-role"],
    ]:
        await ctx.respond(loc["claim"]["UnclaimableRole"])
        return
    elif (
        any(
            ctx.options.role.id in member.role_ids
            for member in ctx.get_guild().get_members().values()
        )
        and ctx.options.role.name.lower() in gamedata.CHARACTERS
    ):
        await ctx.respond(loc["claim"]["RoleIsTaken"])
        return

    # Check if player already has a character role
    for role_id in ctx.member.role_ids:
        if ctx.get_guild().get_role(role_id).name.lower() in gamedata.CHARACTERS:
            await ctx.respond(loc["claim"]["AlreadyHaveOtherRole"])
            return

    # Give role and update player's nickname
    await ctx.member.add_role(ctx.options.role)
    await ctx.respond(loc["claim"]["UpdatedRoles"])
    if ctx.member.id == ctx.get_guild().owner_id:
        # Can't update nickname for server owner
        await ctx.respond(LOCALIZATION_DATA["errors"]["ServerOwnerNicknameChange"])

    elif ctx.options.role.name.lower() in gamedata.CHARACTERS:
        await ctx.member.edit(nick=gamedata.CHARACTERS[ctx.options.role.name.lower()])


@plugin.command()
@lightbulb.command(
    loc["unclaim"]["name"],
    loc["unclaim"]["description"],
    aliases=loc["unclaim"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def unclaim(ctx: lightbulb.Context) -> None:
    """Remove character roles"""
    for role_id in ctx.member.role_ids:
        role = ctx.get_guild().get_role(role_id)
        if role.name.lower() in gamedata.CHARACTERS:
            await ctx.member.remove_role(role)
            await ctx.respond(f"Removed role {role.name}")
            if ctx.author.id == ctx.get_guild().owner_id:
                # Can't update nickname for server owner
                await ctx.respond(
                    LOCALIZATION_DATA["errors"]["ServerOwnerNicknameChange"]
                )

            else:
                await ctx.author.edit(nick=None)
            return
    await ctx.respond(LOCALIZATION_DATA["errors"]["NoCharacterRoles"])


@plugin.command()
@lightbulb.command(
    loc["roles"]["name"], loc["roles"]["description"], aliases=loc["roles"]["aliases"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def roles(ctx: lightbulb.Context) -> None:
    """Displays your roles"""

    message = loc["roles"]["YourRoles"] + "\n"
    message += ", ".join(
        ctx.get_guild().get_role(role_id).name
        for role_id in ctx.member.role_ids
        if role_id != ctx.guild_id
    )
    await ctx.respond(message)


@plugin.command()
@lightbulb.command(
    loc["users"]["name"], loc["users"]["description"], aliases=loc["users"]["aliases"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def users(ctx: lightbulb.Context) -> None:
    """Lists all players and spectators"""
    game = ctx.bot.d.games[ctx.guild_id]
    message = ""
    spectators = [
        member
        for member in game.guild.get_members().values()
        if game.spectator_role.id in member.role_ids
    ]
    if spectators:
        message += loc["users"]["spectators"]
        message += "\n"
        message += ", ".join(member.display_name for member in spectators)
        message += "\n"
    if game.char_roles():
        message += loc["users"]["players"]
        message += "\n"
        message += ", ".join(role.name for role in game.char_roles().values())
    await ctx.respond(message or loc["users"]["NoneFound"])


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
