# Built-in
import asyncio
# 3rd-party
import discord
from discord.ext import commands
# Local
import gamedata

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        """Only let server admins run"""
        return ctx.author.guild_permissions.administrator
    
    @commands.command()
    async def show_all(self, ctx):
        """Allows all members to read every channel and disables sending"""

        for channel in ctx.guild.text_channels:
            await channel.edit(sync_permissions=True)
        await ctx.send("All channels revealed!")

    @commands.command(aliases=["clear"])
    async def wipe(self, ctx, *text_channels: discord.TextChannel):
        """Erases all messages and clears game data"""

        # Confirm command to user
        await ctx.send("Deleting all messages!")

        # Wipe messages
        if not text_channels:
            text_channels = ctx.guild.text_channels
        for text_channel in text_channels:
            asyncio.create_task(text_channel.purge(limit=None))

        # Reset game data
        ctx.game.__init__(ctx.game.guild)

        # Console logging
        print(f'Wiped messages from server: "{ctx.guild.name}" with ID: "{ctx.guild.id}"')

    @commands.command()
    async def reset_perms(self, ctx):
        """Resets channel permissions to the default"""

        everyone = ctx.guild.default_role
        spectator = ctx.game.spectator_role

        for channel in ctx.guild.text_channels:
            if "-clues" in channel.name:
                await channel.set_permissions(everyone, view_channel=False, send_messages=False)
                await channel.set_permissions(spectator, view_channel=True)

                player = channel.name.split("-")[0].title()
                for role in ctx.guild.roles:
                    if role.name == player:
                        await channel.set_permissions(role, view_channel=True)
            
            elif channel.name == "voicemails" or channel.name == "group-chat":
                await channel.set_permissions(everyone, send_messages=False)
                for role in ctx.guild.roles:
                    if role.name.lower() in gamedata.CHARACTERS:
                        await channel.set_permissions(role, send_messages=True)

            elif channel.name == "group-chat":
                await channel.set_permissions(everyone, send_messages=None)
                await channel.set_permissions(spectator, send_messages=False)

            elif "-pm" in channel.name:
                await channel.set_permissions(everyone, view_channel=False, send_messages=None)
                await channel.set_permissions(spectator, view_channel=True, send_messages=False)
                split_name = channel.name.split("-")
                player_a = split_name[0].title()
                player_b = split_name[1].title()
                for role in ctx.guild.roles:
                    if role.name == player_a or role.name == player_b:
                        await channel.set_permissions(role, view_channel=True)

    @commands.command()
    async def reset(self, ctx):
        """Resets server, including channel permissions"""

        # Confirm command to user
        await ctx.send("Resetting the server!")

        # Console logging
        print(f'Resetting server: "{ctx.guild.name}" with ID: "{ctx.guild.id}"')

        # Erase all messages
        await self.wipe(ctx)

        # Reset channel permissions
        await self.reset_perms(ctx)


def setup(bot):
    bot.add_cog(Admin(bot))
