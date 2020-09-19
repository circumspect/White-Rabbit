import discord
from discord.ext import commands


class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.command()
    async def load(self, ctx, extension_name: str = "all"):
        """Loads an extension."""
        if extension_name == "all":
            loaded_extensions = list(self.bot.extensions.keys())
            for extension in loaded_extensions:
                self.bot.reload_extension(extension)
            await ctx.send(f"reloaded {', '.join(loaded_extensions)}")
            return

        # load extension
        try:
            if extension_name in self.bot.extensions:
                self.bot.reload_extension(extension_name)
            else:
                self.bot.load_extension(extension_name)
            await ctx.send(f"loaded {extension_name}")
        except discord.ext.commands.errors.ExtensionNotFound:
            await ctx.send(f"could not find {extension_name}")

    @commands.command()
    async def unload(self, ctx, extension_name: str):
        """Unloads an extension."""
        self.bot.unload_extension(extension_name)
        await ctx.send(f"unloaded {extension_name}")

    @commands.command()
    async def quit(self, ctx):
        """Unloads an extension."""
        await ctx.send("quitting")
        await self.bot.close()


def setup(bot):
    bot.add_cog(Dev(bot))
