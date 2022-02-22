import asyncio

import hikari
import lightbulb
from hikari import permissions
from lightbulb import commands, converters

from utils import constants, gamedata, miscutils
from utils.localization import LOCALIZATION_DATA

plugin = lightbulb.Plugin("Admin")
plugin.add_checks(lightbulb.has_guild_permissions(permissions.Permissions.ADMINISTRATOR))

loc = LOCALIZATION_DATA["commands"]["admin"]
GROUP_CHAT = LOCALIZATION_DATA["channels"]["texts"]["group-chat"]


@plugin.command()
@lightbulb.command(loc["show_all"]["name"], loc["show_all"]["description"], aliases=loc["show_all"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def show_all(ctx: lightbulb.Context) -> None:
    """Reveal all channels and disable sending messages"""
    for channel in ctx.get_guild().get_channels().values():
        if channel.type != hikari.ChannelType.GUILD_TEXT or not channel.parent_id:
            continue
        parent = ctx.get_guild().get_channel(channel.parent_id)
        await channel.edit(permission_overwrites=parent.permission_overwrites.values())


@plugin.command()
@lightbulb.option("text_channels", "channels to wipe", type=hikari.TextableGuildChannel, modifier=commands.OptionModifier.GREEDY, required=False)
@lightbulb.command(loc["wipe"]["name"], loc["wipe"]["description"], aliases=loc["wipe"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def wipe(ctx: lightbulb.Context) -> None:
    """Erases all messages and clears game data"""
    # Confirm command to user
    await ctx.respond(loc["wipe"]["DeletingMessages"])

    # Wipe messages
    text_channels = ctx.options.text_channels
    if not text_channels:
        text_channels = miscutils.get_text_channels(ctx.get_guild()).values()
    for text_channel in text_channels:
        await ctx.bot.rest.delete_messages(text_channel.id, await ctx.bot.rest.fetch_messages(text_channel.id))

    # Reset game data
    game = ctx.bot.d.games[ctx.guild_id]
    game.__init__(game.guild)

    # Console logging
    print(f'{constants.INFO_PREFIX}Wiped messages from server: "{ctx.get_guild().name}" (ID: {ctx.guild_id})')

@plugin.command()
@lightbulb.command(loc["reset_perms"]["name"], loc["reset_perms"]["description"], aliases=loc["reset_perms"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def reset_perms(ctx: lightbulb.Context) -> None:
    """Resets channel permissions to the default (undoes !show_all)"""

    everyone = ctx.get_guild().get_role(ctx.guild_id)
    spectator = ctx.bot.d.games[ctx.guild_id].spectator_role

    for channel in miscutils.get_text_channels(ctx.get_guild()).values():
        # Clues channels
        if channel.name in LOCALIZATION_DATA["channels"]["clues"].values():
            await channel.edit_overwrite(
                everyone,
                deny=hikari.Permissions.VIEW_CHANNEL | hikari.Permissions.SEND_MESSAGES,
            )
            await channel.edit_overwrite(spectator, allow=hikari.Permissions.VIEW_CHANNEL)

            player = channel.name.split("-")[0].title()
            for role in ctx.get_guild().get_roles().values():
                if role.name == player:
                    asyncio.create_task(channel.edit_overwrite(role, allow=hikari.Permissions.VIEW_CHANNEL))

        # Channels where all players can send messages
        elif channel.name in [GROUP_CHAT, LOCALIZATION_DATA["channels"]["voicemails"]]:
            asyncio.create_task(channel.edit_overwrite(
                everyone,
                deny=hikari.Permissions.SEND_MESSAGES,
            ))
            for role in ctx.get_guild().get_roles().values():
                if role.name.lower() in gamedata.CHARACTERS:
                    asyncio.create_task(channel.edit_overwrite(role, allow=hikari.Permissions.SEND_MESSAGES))

        # Private message channels
        elif channel.name in LOCALIZATION_DATA["channels"]["texts"].values() and channel.name != GROUP_CHAT:
            asyncio.create_task(channel.edit_overwrite(
                everyone,
                deny=hikari.Permissions.VIEW_CHANNEL,
            ))
            asyncio.create_task(channel.edit_overwrite(
                spectator,
                allow=hikari.Permissions.VIEW_CHANNEL,
                deny=hikari.Permissions.SEND_MESSAGES,
            ))
            player_a, player_b, *_ = channel.name.split("-")
            for role in ctx.get_guild().get_roles().values():
                if role.name.lower() in [player_a, player_b]:
                    asyncio.create_task(channel.edit_overwrite(role, allow=hikari.Permissions.VIEW_CHANNEL))

@plugin.command()
@lightbulb.command(loc["reset_roles"]["name"], loc["reset_roles"]["description"], aliases=loc["reset_roles"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def reset_roles(ctx: lightbulb.Context) -> None:
    # Removes character roles from everyone
    for member in ctx.guild.members:
        is_player = False
        if not member.bot:
            for role in member.roles:
                if role.name.lower() in gamedata.CHARACTERS.keys():
                    await member.remove_roles(role)
                    is_player = True
            if is_player:
                if member is ctx.guild.owner:
                    await ctx.respond(loc["reset_roles"]["NoteAboutOwner"])
                else:
                    await member.edit(nick=None)

@plugin.command()
@lightbulb.command(loc["reset"]["name"], loc["reset"]["description"], aliases=loc["reset"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def reset(ctx: lightbulb.Context) -> None:
    """Complete server reset"""

    # Confirm command to user
    await ctx.respond(loc["reset"]["ResettingServer"])

    # Console logging
    print(f'{constants.INFO_PREFIX}Resetting server: "{ctx.guild.name}" (ID: {ctx.guild.id})')

    # Erase all messages and reset channel permissions
    await asyncio.gather(wipe(ctx), reset_perms(ctx), reset_roles(ctx))




def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
