# Built-in
import asyncio
import random
import time
# 3rd-party
import discord
from discord.ext import commands, tasks


class Game:
    def __init__(self, guild):
        self.guild = guild
        self.setup = False
        self.started = False
        self.show_timer = False


class Admin(commands.Cog):
    CHARACTERS = (
        "Charlie Barnes", "Dakota Travis", "Evan Holwell",
        "Jack Briarwood", "Julia North"
    )
    GAME_LENGTH = 90 * 60
    TIMER_GAP = 10

    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    async def cog_before_invoke(self, ctx):
        ctx.game = self.games.setdefault(ctx.guild.id, Game(ctx.guild))
        ctx.text_channels = {
            channel.name: channel
            for channel in ctx.guild.text_channels
        }

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot has logged in")
        self.timer.start()

    @commands.command()
    async def start(self, ctx):
        """Begins the game"""

        if not ctx.game.setup:
            await ctx.send("Can't start before setting up!")
            return

        if ctx.game.started:
            await ctx.send("Game has already begun!")
            return

        ctx.game.start_time = time.time()
        ctx.game.started = True
        await ctx.send("Starting the game!")

    @commands.command(name="timer")
    async def show_time(self, ctx):
        """Toggle bot timer"""

        ctx.game.show_timer = not ctx.game.show_timer
        if ctx.game.show_timer:
            await ctx.send("Showing bot timer!")
        else:
            await ctx.send("Hiding bot timer!")

    @tasks.loop(seconds=TIMER_GAP)
    async def timer(self):
        for game in self.games.values():
            # Skip if game has not started
            if not game.started:
                continue
            # Skip if game has ended
            if game.start_time + self.GAME_LENGTH < time.time():
                continue

            remaining_time = game.start_time + self.GAME_LENGTH - time.time()

            if game.show_timer:
                text_channels = {
                    channel.name: channel
                    for channel in game.guild.text_channels
                }
                await text_channels["bot-channel"].send((
                    f"{str(int(remaining_time // 60)).zfill(2)}:{str(int(remaining_time % 60)).zfill(2)}"
                ))

    @commands.command()
    async def setup(self, ctx):
        """Sends out cards and sets up the game"""

        if ctx.game.started:
            await ctx.send("Game has already begun!")
            return

        await ctx.send("Starting setup")

        # Character cards in character channel
        for character in self.CHARACTERS:
            asyncio.create_task(ctx.text_channels["character-cards"].send(file=discord.File(
                f"Images/Cards/Characters/{character.title()}.png"
            )))

        # Character and motive cards in clues channels
        motives = list(range(1, 6))
        random.shuffle(motives)
        for character, motive in zip(self.CHARACTERS, motives):
            channel = ctx.text_channels[f"{character.lower().split()[0]}-clues"]
            asyncio.create_task(channel.send(file=discord.File(
                f"Images/Cards/Characters/{character.title()}.png"
            )))
            asyncio.create_task(channel.send(file=discord.File(
                f"Images/Cards/Motives/Motive {motive}.png"
            )))
        
        # 90 minute card for Charlie Barnes
        channel = ctx.text_channels["charlie-clues"]
        asyncio.create_task(channel.send(file=discord.File(
            "Images/Cards/Clues/90/90-1.png"
        )))
        first_message = "Hey! Sorry for the big group text, but I just got "\
                        "into town for winter break at my dad's "\
                        "and haven't been able to get ahold of Alice. Just "\
                        "wondering if any of you have spoken to her?"
        asyncio.create_task(channel.send(first_message))

        ctx.game.setup = True

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
