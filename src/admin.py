# 3rd-party
import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @ commands.command()
    async def wipe(self, ctx, *text_channels: discord.TextChannel):
        """Wipes all messages on the server"""

        if not text_channels:
            text_channels = ctx.guild.text_channels
        for text_channel in text_channels:
            await text_channel.purge(limit=None)


def setup(bot):
    bot.add_cog(Admin(bot))
