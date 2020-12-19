
import asyncio

import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        """Only let server admins run"""
        return ctx.author.guild_permissions.administrator

    @commands.command(aliases=["wipe"])
    async def reset(self, ctx, *text_channels: discord.TextChannel):
        """Resets server and game data"""

        # Confirm command to user
        await ctx.send("Resetting the server!")

        # Console logging
        print(f'Resetting server: "{ctx.guild.name}" with ID: "{ctx.guild.id}"')

        # wipe
        if not text_channels:
            text_channels = ctx.guild.text_channels
        for text_channel in text_channels:
            asyncio.create_task(text_channel.purge(limit=None))

        # Console logging
        print(f'Wiped messages from server: "{ctx.guild.name}" with ID: "{ctx.guild.id}"')

        # Reset game data
        ctx.game.__init__(ctx.game.guild)


def setup(bot):
    bot.add_cog(Admin(bot))
