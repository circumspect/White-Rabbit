# Built-in
import asyncio
import itertools as it
# 3rd-party
import discord
from discord.ext import commands
from discord.permissions import PermissionOverwrite
# Local
from data import cards, constants
from data.wrappers import Bot, Context
from data.localization import LOCALIZATION_DATA

loc = LOCALIZATION_DATA["commands"]["admin"]
GROUP_CHAT = LOCALIZATION_DATA["channels"]["texts"]["group-chat"]

PERMS_NO_READING = PermissionOverwrite()
PERMS_NO_READING.update(**{"read_messages": False})
PERMS_NO_SENDING = PermissionOverwrite()
PERMS_NO_SENDING.update(**{"send_messages": False})
PERMS_YES_READING = PermissionOverwrite()
PERMS_YES_READING.update(**{"read_messages": True})
PERMS_YES_SENDING = PermissionOverwrite()
PERMS_YES_SENDING.update(**{"send_messages": True})
PERMS_NO_ACCESS = PermissionOverwrite()
PERMS_NO_ACCESS.update(**{"read_messages": False, "send_messages": False})
PERMS_SPECTATOR = PermissionOverwrite()
PERMS_SPECTATOR.update(**{"read_messages": True, "send_messages": False})

class Admin(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        """Commands for server admins only"""

        return ctx.author.guild_permissions.administrator

    @commands.command(
        name=loc["server_setup"]["name"],
        aliases=loc["server_setup"]["aliases"],
        description=loc["server_setup"]["description"]
    )
    async def server_setup(self, ctx: Context):
        """Deletes all channels and roles and creates new ones based on the given card list"""

        assert ctx.guild is not None

        # Delete roles and channels
        async_tasks = []
        for role in ctx.guild.roles:
            if role.name != "The White Rabbit" and role != ctx.guild.default_role:
                async_tasks.append(role.delete())

        for channel in ctx.guild.text_channels:
            # if channel.name != LOCALIZATION_DATA["channels"]["bot-channel"]:
            async_tasks.append(channel.delete())
        for channel in ctx.guild.categories:
            async_tasks.append(channel.delete())
        for channel in ctx.guild.voice_channels:
            async_tasks.append(channel.delete())

        await asyncio.gather(*async_tasks)

        # Create roles
        roles = {}

        for name, character in cards.CHARACTERS.items():
            roles[name] = await ctx.guild.create_role(name=character.role)

        ctx.game.spectator_role = await ctx.guild.create_role(name=LOCALIZATION_DATA["spectator-role"])
        roles["spectator"] = ctx.game.spectator_role

        # TODO: Localization
        channel_categories = {
            "general": await ctx.guild.create_category(LOCALIZATION_DATA["categories"]["general"]),
            "game": await ctx.guild.create_category(LOCALIZATION_DATA["categories"]["game"],
                overwrites = {
                    ctx.guild.default_role: PERMS_NO_SENDING
                }
            ),
            "texts": await ctx.guild.create_category(LOCALIZATION_DATA["categories"]["texts"],
                overwrites = { ctx.guild.default_role: PERMS_NO_SENDING }
            )
        }

        # General channels are open to everyone
        await ctx.guild.create_text_channel(
            LOCALIZATION_DATA["channels"]["discussion"],
            category = channel_categories["general"]
        )
        await ctx.guild.create_text_channel(
            LOCALIZATION_DATA["channels"]["bot-channel"],
            category = channel_categories["general"]
        )
        await ctx.guild.create_voice_channel(
            LOCALIZATION_DATA["channels"]["call"],
            category = channel_categories["general"]
        )

        # Game channels don't allow sending, except in voicemails
        await ctx.guild.create_text_channel(
            LOCALIZATION_DATA["channels"]["resources"],
            category = channel_categories["game"],
            overwrites = { ctx.guild.default_role: PERMS_NO_SENDING }
        )

        for _, name in LOCALIZATION_DATA["channels"]["cards"].items():
            await ctx.guild.create_text_channel(
                name,
                category = channel_categories["game"],
                overwrites = { ctx.guild.default_role: PERMS_NO_SENDING }
            )

        # Clues
        for character in cards.CHARACTERS:
            await ctx.guild.create_text_channel(
                LOCALIZATION_DATA["channels"]["clues"][character],
                category = channel_categories["game"],
                overwrites = {
                    ctx.guild.default_role: PERMS_NO_ACCESS,
                    roles["spectator"]: PERMS_YES_READING,
                    roles[character]: PERMS_YES_READING,
                }
            )

        # Voicemails
        overwrites = { roles[character]: PERMS_YES_SENDING for character in cards.CHARACTERS }
        overwrites[ctx.guild.default_role] = PERMS_NO_SENDING
        await ctx.guild.create_text_channel(
            LOCALIZATION_DATA["channels"]["voicemails"],
            category = channel_categories["game"],
            overwrites = overwrites
        )

        # Group chat
        overwrites = { roles[character]: PERMS_YES_SENDING for character in cards.CHARACTERS }
        overwrites[ctx.guild.default_role] = PERMS_NO_SENDING
        await ctx.guild.create_text_channel(
            LOCALIZATION_DATA["channels"]["group-chat"],
            category = channel_categories["texts"],
            overwrites = overwrites
        )


        # Private message channels

        for (c1, c2) in it.combinations(cards.CHARACTERS, 2):
            channel = await ctx.guild.create_text_channel(
                LOCALIZATION_DATA["channels"]["texts"][f"{c1}-{c2}"],
                category = channel_categories["texts"],
                overwrites = {
                    ctx.guild.default_role: PERMS_NO_READING,
                    roles["spectator"]: PERMS_SPECTATOR,
                    roles[c1]: PERMS_YES_READING,
                    roles[c2]: PERMS_YES_READING,
                }
            )


    @commands.command(
        name=loc["show_all"]["name"],
        aliases=loc["show_all"]["aliases"],
        description=loc["show_all"]["description"]
    )
    async def show_all(self, ctx: Context):
        """Reveal all channels and disable sending messages"""

        assert ctx.guild is not None

        for channel in ctx.guild.text_channels:
            asyncio.create_task(channel.edit(sync_permissions=True))
        await ctx.send("All channels revealed!")

    @commands.command(
        name=loc["wipe"]["name"],
        aliases=loc["wipe"]["aliases"],
        description=loc["wipe"]["description"]
    )
    async def wipe(self, ctx: Context, *text_channels: discord.TextChannel):
        """Erases all messages and clears game data"""

        assert ctx.guild is not None

        # Confirm command to user
        await ctx.send(loc["wipe"]["DeletingMessages"])

        # Wipe messages
        if not text_channels:
            text_channels = ctx.guild.text_channels
        for text_channel in text_channels:
            asyncio.create_task(text_channel.purge(limit=None))

        # Reset game data
        ctx.game.__init__(ctx.game.guild)

        # Console logging
        print(f'{constants.INFO_PREFIX}Wiped messages from server: "{ctx.guild.name}" (ID: {ctx.guild.id})')

    @commands.command(
        name=loc["reset_perms"]["name"],
        aliases=loc["reset_perms"]["aliases"],
        description=loc["reset_perms"]["description"]
    )
    async def reset_perms(self, ctx: Context):
        """Resets channel permissions to the default (undoes !show_all)"""

        assert ctx.guild is not None

        everyone = ctx.guild.default_role
        spectator = ctx.game.spectator_role

        for channel in ctx.guild.text_channels:
            # Clues channels
            if channel.name in LOCALIZATION_DATA["channels"]["clues"].values():
                asyncio.create_task(channel.set_permissions(
                    everyone,
                    view_channel=False,
                    send_messages=False
                ))
                asyncio.create_task(channel.set_permissions(spectator, view_channel=True))

                player = channel.name.split("-")[0].title()
                for role in ctx.guild.roles:
                    if role.name == player:
                        asyncio.create_task(channel.set_permissions(role, view_channel=True))

            # Channels that all players can send messages
            elif channel.name in [GROUP_CHAT, LOCALIZATION_DATA["channels"]["voicemails"]]:
                asyncio.create_task(channel.set_permissions(everyone, send_messages=False))
                for role in ctx.guild.roles:
                    if role.name in cards.ROLES_TO_NAMES:
                        asyncio.create_task(channel.set_permissions(role, send_messages=True))

            # Private message channels
            elif channel.name in LOCALIZATION_DATA["channels"]["texts"].values() and channel.name != GROUP_CHAT:
                asyncio.create_task(channel.set_permissions(everyone, view_channel=False, send_messages=None))
                asyncio.create_task(channel.set_permissions(spectator, view_channel=True, send_messages=False))
                split_name = channel.name.split("-")
                player_a = split_name[0].title()
                player_b = split_name[1].title()
                for role in ctx.guild.roles:
                    if role.name in [player_a, player_b]:
                        asyncio.create_task(channel.set_permissions(role, view_channel=True))

    @commands.command(
        name=loc["reset_roles"]["name"],
        aliases=loc["reset_roles"]["aliases"],
        description=loc["reset_roles"]["description"]
    )
    async def reset_roles(self, ctx: Context):
        assert ctx.guild is not None

        # Removes character roles from everyone
        for member in ctx.guild.members:
            is_player = False
            if not member.bot:
                for role in member.roles:
                    if role.name in cards.ROLES_TO_NAMES:
                        await member.remove_roles(role)
                        is_player = True
                if is_player:
                    if member is ctx.guild.owner:
                        await ctx.send(loc["reset_roles"]["NoteAboutOwner"])
                    else:
                        await member.edit(nick=None)

    @commands.command(
        name=loc["reset"]["name"],
        aliases=loc["reset"]["aliases"],
        description=loc["reset"]["description"]
    )
    async def reset(self, ctx: Context):
        """Complete server reset"""

        assert ctx.guild is not None

        # Confirm command to user
        await ctx.send(loc["reset"]["ResettingServer"])

        # Console logging
        print(f'{constants.INFO_PREFIX}Resetting server: "{ctx.guild.name}" (ID: {ctx.guild.id})')

        # Erase all messages and reset channel permissions
        await asyncio.gather(self.wipe(ctx), self.reset_perms(ctx), self.reset_roles(ctx))


async def setup(bot: Bot):
    await bot.add_cog(Admin(bot))
