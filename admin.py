# Built-in
import asyncio
import random
import time
# 3rd-party
import discord
from discord.ext import commands, tasks


class Admin(commands.Cog):
    CHARACTERS = (
        "Charlie Barnes", "Dakota Travis", "Evan Holwell",
            "Jack Briarwood", "Julia North"
    )
    GAME_LENGTH = 90 * 60
    TIMER_GAP = 10
    
    def __init__(self, bot):
        self.bot = bot
        self.setup = False
        self.started = False
        self.show_timer = False

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.text_channels = {
            channel.name: channel
            for channel in self.bot.guilds[0].text_channels
        }
        print(f"Bot has logged in")

    @commands.command()
    async def start(self, ctx):
        """Begins the game"""
        
        if not self.setup:
            await ctx.send("Can't start before setting up!")
            return
        
        if self.started:
            await ctx.send("Game has already begun!")
            return

        self.start_time = time.time()
        self.timer.start()
        self.started = True
        await ctx.send("Starting the game!")

    @commands.command()
    async def show_time(self, ctx):
        """Toggle bot timer"""

        self.show_timer = not self.show_timer
        if self.show_timer:
            await ctx.send("Bot timer enabled!")
        else:
            await ctx.send("Bot timer disabled!")


    @tasks.loop(seconds=TIMER_GAP)
    async def timer(self):
        # Stop if game has ended
        if self.start_time + self.GAME_LENGTH < time.time():
            self.timer.cancel()

        remaining_time = self.start_time + self.GAME_LENGTH - time.time()
        
        if self.show_timer:
            await self.text_channels["bot-channel"].send((
                f"{str(int(remaining_time // 60)).zfill(2)}:{str(int(remaining_time % 60)).zfill(2)}"
            ))

    @commands.command()
    async def setup(self, ctx):
        """Sends out cards and sets up the game"""

        if self.started:
            await ctx.send("Game has already begun!")
            return

        motives = list(range(1, 6))
        random.shuffle(motives)
        for character, motive in zip(self.CHARACTERS, motives):
            channel = self.text_channels[f"{character.lower().split()[0]}-clues"]
            asyncio.ensure_future(channel.send(file=discord.File(
                f"Images/Cards/Characters/{character.title()}.png"
            )))
            asyncio.ensure_future(channel.send(file=discord.File(
                f"Images/Cards/Motives/Motive {motive}.png"
            )))
        self.setup = True
        await ctx.send("Running setup")

    @commands.command()
    async def wipe(self, ctx, *text_channels: discord.TextChannel):
        """Wipes all messages on the server"""

        if not text_channels:
            text_channels = ctx.guild.text_channels
        for text_channel in text_channels:
            await text_channel.purge(limit=None)

    @commands.command()
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

    @commands.command()
    async def unload(self, ctx, extension_name: str):
        """Unloads an extension."""

        self.bot.unload_extension(extension_name)
        await ctx.send(f"Unloaded {extension_name}")

    @commands.command()
    async def quit(self, ctx):
        """Quits the bot"""
        
        await ctx.send("Thanks for playing!")
        await self.bot.close()



def setup(bot):
    bot.add_cog(Admin(bot))
