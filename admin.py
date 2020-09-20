# 3rd-party
import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot has logged in")

    @ commands.command()
    async def wipe(self, ctx, *text_channels: discord.TextChannel):
        """Wipes all messages on the server"""

        if not text_channels:
            text_channels = ctx.guild.text_channels
        for text_channel in text_channels:
            await text_channel.purge(limit=None)

    @ commands.command()
    async def load(self, ctx, extension_name: str = "all"):
        """(Re)loads an extension"""

        if extension_name == "all":
            loaded_extensions = list(self.bot.extensions.keys())
            for extension in loaded_extensions:
                self.bot.reload_extension(extension)
            await ctx.send(f"Reloaded {', '.join(loaded_extensions)}")
            return

        # Load extension
        try:
            if extension_name in self.bot.extensions:
                self.bot.reload_extension(extension_name)
            else:
                self.bot.load_extension(extension_name)
            await ctx.send(f"Loaded {extension_name}")
        except discord.ext.commands.errors.ExtensionNotFound:
            await ctx.send(f"Couldn't find {extension_name}")

    @ commands.command()
    async def unload(self, ctx, extension_name: str):
        """Unloads an extension."""

        self.bot.unload_extension(extension_name)
        await ctx.send(f"Unloaded {extension_name}")

    @ commands.command()
    async def quit(self, ctx):
        """Quits the bot"""

        await ctx.send("Thanks for playing!")
        await self.bot.close()


def setup(bot):
    bot.add_cog(Admin(bot))
