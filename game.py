# Built-in
import asyncio
import os
import random
import time
import glob
# 3rd-party
import discord
from discord.ext import commands, tasks
# Local
import gamedata


class Game(commands.Cog):
    def __init__(self, bot):
        self.games = {}

    async def cog_before_invoke(self, ctx):
        ctx.game = self.games.setdefault(ctx.guild.id, gamedata.Data(ctx.guild))
        ctx.text_channels = {
            channel.name: channel
            for channel in ctx.guild.text_channels
        }

    @commands.Cog.listener()
    async def on_ready(self):
        self.timer.start()

    @commands.command()
    async def setup(self, ctx):
        """Sends out cards and sets up the game"""
        def send_image(channel, filepath):
            if isinstance(channel, str):
                channel = ctx.text_channels[channel]
            asyncio.create_task(channel.send(
                file=discord.File(filepath)
            ))

        def send_folder(channel, path):
            for image in sorted(os.scandir(path), key=lambda x: x.name):
                send_image(channel, os.path.join(path, image.name))

        if ctx.game.started:
            await ctx.send("Game has already begun!")
            return

        await ctx.send("Starting setup")

        # Introduction images
        send_image("player-resources", "Images/Player Resources/Alice is Missing - Guide.jpg")
        send_image("player-resources", "Images/Player Resources/Alice is Missing - Character Sheet.jpg")
        send_image("player-resources", "Images/Cards/Misc/Introduction.png")
        alice = random.choice(glob.glob("Images/Missing Person Posters/*.png"))
        send_image("player-resources", alice)

        # Send characters, suspects, and locations to appropriate channels
        send_folder("character-cards", gamedata.CHARACTER_IMAGE_DIR)
        send_folder("suspect-cards", gamedata.SUSPECT_IMAGE_DIR)
        send_folder("location-cards", gamedata.LOCATION_IMAGE_DIR)

        # Character and motive cards in clues channels
        motives = list(range(1, 6))
        random.shuffle(motives)
        for character, motive in zip(gamedata.CHARACTERS.values(), motives):
            channel = ctx.text_channels[f"{character.lower().split()[0]}-clues"]
            send_image(channel, f"Images/Cards/Characters/{character}.png")
            send_image(channel, f"Images/Cards/Motives/Motive {motive}.png")

        # 90 minute card for Charlie Barnes
        channel = ctx.text_channels["charlie-clues"]
        asyncio.create_task(channel.send(file=discord.File(
            "Images/Cards/Clues/90/90-1.png"
        )))
        first_message = "Hey! Sorry for the big group text, but I just got "\
                        "into town for winter break at my dad's and haven't "\
                        "been able to get ahold of Alice. Just wondering if "\
                        "any of you have spoken to her?"
        prompts = "\n".join([
            "Read introduction", "Introduce alice from poster",
            "Introduce/pick characters", "Explain character cards",
            "Explain drive cards", "Character introductions (relationships)",
            "Voicemails", "Suspects and locations", "Explain clue cards",
            "Explain searching", "game guide",
            "setup playlist https://www.youtube.com/watch?v=ysOOFIOAy7A",
            "Run !start", "90 min card",
        ])
        asyncio.create_task(channel.send(f"```{prompts}```"))
        asyncio.create_task(channel.send(first_message))

        ctx.game.setup = True

    @commands.command()
    async def shuffle_clues(self, ctx):
        """Randomizes and assigns clue times"""
        for character in gamedata.CHARACTERS:
            pass

    @commands.command()
    async def start(self, ctx):
        """Begins the game"""

        if not ctx.game.setup:
            await ctx.send("Can't start before setting up!")
            return

        if ctx.game.started:
            await ctx.send("Game has already begun!")
            return

        if len(ctx.game.char_roles) < 3:
            await ctx.send("Not enough players")
            return

        ctx.game.start_time = time.time()
        ctx.game.started = True
        await ctx.send("Starting the game!")

    @commands.command(name="timer")
    async def show_time(self, ctx):
        """Show/hide bot timer"""

        ctx.game.show_timer = not ctx.game.show_timer
        if ctx.game.show_timer:
            await ctx.send("Showing bot timer!")
        else:
            await ctx.send("Hiding bot timer!")

    @tasks.loop(seconds=gamedata.TIMER_GAP)
    async def timer(self):
        for game in self.games.values():
            # Skip if game has not started
            if not game.started:
                continue
            # Skip if game has ended
            if game.start_time + gamedata.GAME_LENGTH < time.time():
                continue

            remaining_time = game.start_time + gamedata.GAME_LENGTH - time.time()

            if game.show_timer:
                text_channels = {
                    channel.name: channel
                    for channel in game.guild.text_channels
                }
                await text_channels["bot-channel"].send((
                    f"{str(int(remaining_time // 60)).zfill(2)}:{str(int(remaining_time % 60)).zfill(2)}"
                ))

    @commands.command()
    async def search(self, ctx):
        if not ctx.game.started:
            await ctx.send("The game hasn't started yet")
        for role in ctx.author.roles:
            if role.name.lower() in gamedata.CHARACTERS:
                character = role.name.lower()
                break
        else:
            await ctx.send("You don't have a character role")
            return

        search_card = random.choice(glob.glob("Images/Cards/Searching/*.png"))
        asyncio.create_task(ctx.text_channels[f"{character}-clues"].send(
            file=discord.File(search_card)
        ))


def setup(bot):
    bot.add_cog(Game(bot))
