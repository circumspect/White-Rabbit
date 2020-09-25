import asyncio

import discord
from discord.ext import commands

import gamedata
import utils


class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(utils.WHITE_RABBIT_DIR / "dev_ids.txt") as f:
            self.dev_ids = [int(line.strip()) for line in f.readlines()]

    async def cog_check(self, ctx):
        """Only people with access to the code"""
        return ctx.author.id in self.dev_ids

    @commands.Cog.listener()
    async def on_ready(self):
        # Console logging
        print("Bot has logged in!")

    @ commands.command()
    async def speed(self, ctx, speed: int = 1):
        """Changes the speed of the game - DEBUG USE ONLY"""

        ctx.game.game_speed = speed

        # Set timer to only ping once every minute to avoid discord api limits
        ctx.game.timer_gap = 60

        # Cap the top speed
        if speed > gamedata.MAX_SPEED:
            asyncio.create_task(ctx.send(f"Too fast! Max is {gamedata.MAX_SPEED}"))
            return

        if speed == 1:
            asyncio.create_task(ctx.send("Reset the game speed!"))
        else:
            asyncio.create_task(ctx.send("Set the game speed!"))

    @ commands.command()
    async def plugins(self, ctx):
        """Lists all currently loaded plugins"""

        message = "Plugins loaded:"
        message += "\n".join(self.bot.cogs.keys())
        await ctx.send(f"```{message}```")

    @ commands.command()
    async def load(self, ctx, extension_name: str = "all"):
        """(Re)loads a plugin"""

        extension_name = extension_name.lower()

        # Reload all
        if extension_name == "all":
            for extension in self.bot.extensions.keys():
                self.bot.reload_extension(extension)
            await ctx.send(f"Reloaded {', '.join(self.bot.extensions.keys())}")
            return

        # Load extension
        try:
            if extension_name in self.bot.extensions:
                self.bot.reload_extension(extension_name)
            else:
                self.bot.load_extension(extension_name)
            await ctx.send(f"Loaded {extension_name}")

        except commands.errors.ExtensionNotFound:
            await ctx.send(f"Couldn't find plugin: \"{extension_name}\"")

    @ commands.command()
    async def unload(self, ctx, extension_name: str):
        """Unloads a plugin."""
        try:
            self.bot.unload_extension(extension_name)
            await ctx.send(f"Unloaded {extension_name}")
        except commands.errors.ExtensionNotLoaded:
            await ctx.send(f"{extension_name} was never loaded")

    @ commands.command(aliases=["stop", "shutdown"])
    async def quit(self, ctx):
        """Quits the bot"""

        await ctx.send("Shutting down, thanks for playing!")
        await self.bot.close()


def setup(bot):
    bot.add_cog(Debug(bot))
