# Built-in
import asyncio
import random
import time
import typing
# 3rd-party
import discord
from discord.ext import commands, tasks
# Local
import filepaths
import gamedata
import manual


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.timer.start()

    @commands.command()
    async def auto(self, ctx, mode: str = ""):
        """
        Prints or current mode or turn automatic on/off

        Syntax:
        !auto will display the current mode
        !auto on will switch to automatic mode
        !auto off will switch to manual mode
        Automatic mode will disable manual card draw commands
        """

        if not mode:
            # Print current mode
            message = "```\nCurrent mode: "
            if ctx.game.automatic:
                message += "automatic"
            else:
                message += "manual"
            message += "\n```"
            await ctx.send(message)
        elif mode == "on":
            ctx.game.automatic = True
            await ctx.send("Automatic card draw enabled!")
        elif mode == "off":
            ctx.game.automatic = True
            await ctx.send("Automatic card draw disabled!")
        else:
            await ctx.send("Input error, try !auto on or !auto off")

    def send_image(self, ctx, channel, filepath):
        """Sends an image to a specified channel"""

        if isinstance(channel, str):
            channel = ctx.text_channels[channel]
        asyncio.create_task(channel.send(
            file=discord.File(filepath)
        ))

    def send_folder(self, ctx, channel, path):
        """Sends all images in a folder in alphabetical order"""
        
        for image in sorted(path.glob("*")):
            self.send_image(ctx, channel, image)

    @commands.command()
    async def setup(self, ctx):
        """Sends out cards and sets up the game"""

        if ctx.game.started:
            await ctx.send("Game has already begun!")
            return
        elif ctx.game.setup:
            await ctx.send("Setup already run!")
            return

        await ctx.send("Starting setup")

        # Introduction images
        self.send_image(
            ctx,
            "player-resources",
            filepaths.RESOURCE_DIR / "Alice is Missing - Guide.jpg"
        )
        self.send_image(
            ctx,
            "player-resources",
            filepaths.RESOURCE_DIR / "Alice is Missing - Character Sheet.jpg"
        )
        self.send_image(
            ctx,
            "player-resources",
            filepaths.CARD_DIR / "Misc" / "Introduction.png"
        )
        alice = random.choice(list(
            (filepaths.IMAGE_DIR / "Missing Person Posters").glob("*.png")
        ))
        self.send_image(ctx, "player-resources", alice)

        # Send characters, suspects, and locations to appropriate channels
        self.send_folder(ctx, "character-cards", filepaths.CHARACTER_IMAGE_DIR)
        self.send_folder(ctx, "suspect-cards", filepaths.SUSPECT_IMAGE_DIR)
        self.send_folder(ctx, "location-cards", filepaths.LOCATION_IMAGE_DIR)

        # Instructions for Charlie Barnes
        channel = ctx.text_channels["charlie-clues"]
        prompts = "\n".join([
            "Read introduction", "Introduce Alice from poster",
            "Introduce/pick characters", "Explain character cards",
            "Explain motive cards", "Character introductions (relationships)",
            "Voicemails", "Suspects and locations", "Explain clue cards",
            "Explain searching", "Game guide",
            "Stream timer (https://www.youtube.com/watch?v=ysOOFIOAy7A)",
            "Run !start", "90 min card",
        ])
        asyncio.create_task(channel.send(f"```{prompts}```"))

        # Character and motive cards in clues channels
        for first_name, full_name in gamedata.CHARACTERS.items():
            channel = ctx.text_channels[f"{first_name}-clues"]
            self.send_image(
                ctx,
                channel,
                filepaths.CHARACTER_IMAGE_DIR / f"{full_name}.png"
            )
            if ctx.game.automatic:
                motive = ctx.game.motives[first_name]
                self.send_image(
                    ctx,
                    channel,
                    filepaths.MOTIVE_DIR / f"Motive {motive}.png"
                )

        await self.bot.cogs["Manual"].shuffle_clues(ctx)

        ctx.game.setup = True

    @commands.command()
    async def shuffle_clues(self, ctx):
        """Randomizes and assigns clue times"""

        # Stop if fewer than 3 player roles assigned
        if len(ctx.game.char_roles()) < 3:
            await ctx.send("Not enough players!")
            return

        player_count = len(ctx.game.char_roles())
        acceptable = False
        while not acceptable:
            clue_buckets = self.randomize_clues(player_count)
            acceptable = self.test_clue_buckets(clue_buckets)

        # Give bucket with 90 minute card to Charlie Barnes
        for i in range(len(clue_buckets)):
            for time in clue_buckets[i]:
                if time == 90:
                    charlie_bucket = i # Willy Wonka sends his regards

        bucket_assignments = {}
        bucket_assignments["charlie"] = clue_buckets.pop(charlie_bucket)
        
        # Assign the rest of the buckets randomly
        names = list(ctx.game.char_roles().keys())
        names = [item.lower() for item in names]
        names.pop(0) # Need to remove charlie from list
        random.shuffle(clue_buckets)
        for name in names:
            bucket_assignments[name] = clue_buckets.pop()
        
        # Print in a code block
        message = "```"
        for player in bucket_assignments:
            bucket_assignments[player].sort(reverse=True)
            clues = player.title() + ": " + ", ".join(str(bucket_assignments[player][x]) for x in range(len(bucket_assignments[player]))) + "\n"
            message += clues
        
        message += "```"
        asyncio.create_task(ctx.send(message))

        # Console logging
        print("Randomly assigned clue cards!")
        print(bucket_assignments)
    
    def randomize_clues(self, player_count: int):
        shuffled_clues = list(gamedata.CLUE_TIMES)
        random.shuffle(shuffled_clues)
        clue_buckets = []
        for i in range(player_count):
            clue_buckets.append([])
        for i in range(len(gamedata.BUCKET_SIZES[player_count])):
            for _ in range(gamedata.BUCKET_SIZES[player_count][i]):
                clue_buckets[i].append(shuffled_clues.pop())

        return clue_buckets

    def test_clue_buckets(self, clue_buckets):
        """
        Checks to see if any clue bucket contains two times 
        within 10 minutes of each other
        """

        for bucket in range(len(clue_buckets)):
            for i in range(len(clue_buckets[bucket])):
                start = i+1
                end = len(clue_buckets[bucket])
                for j in range(start, end):
                    diff = clue_buckets[bucket][i]-clue_buckets[bucket][j]
                    diff = abs(diff)
                    if diff <= 10:
                        return False
        
        return True

    @commands.command()
    async def start(self, ctx):
        """Begins the game"""

        # Validity checks
        if not ctx.game.setup:
            await ctx.send("Can't start before setting up!")
            return

        if ctx.game.started:
            await ctx.send("Game has already begun!")
            return

        if "Charlie" not in ctx.game.char_roles():
            await ctx.send("Can't play without Charlie!")
            return

        if len(ctx.game.char_roles()) < 3:
            await ctx.send("Not enough players!")
            return

        # 90 minute card/message for Charlie Barnes
        channel = ctx.text_channels["charlie-clues"]
        asyncio.create_task(channel.send(file=discord.File(
            filepaths.CLUE_DIR / "90/90-1.png"
        )))
        first_message = "Hey! Sorry for the big group text, but I just got "\
                        "into town for winter break at my dad's and haven't "\
                        "been able to get ahold of Alice. Just wondering if "\
                        "any of you have spoken to her?"
        asyncio.create_task(channel.send(first_message))

        ctx.game.start_time = time.time()
        ctx.game.started = True

        if ctx.game.stream_music:
            if ctx.guild.voice_client is None:
                await ctx.guild.voice_channels[0].connect()
            ctx.guild.voice_client.play(
                discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                    filepaths.TIMER_AUDIO
                )
            ))

        await ctx.send("Starting the game!")

    @commands.command(name="timer")
    async def show_time(self, ctx):
        """Show/hide bot timer"""

        ctx.game.show_timer = not ctx.game.show_timer
        if ctx.game.show_timer:
            await ctx.send("Showing bot timer!")
        else:
            await ctx.send("Hiding bot timer!")
    
    @commands.command()
    async def music(self, ctx):
        """Enable/disable music stream when game starts"""

        ctx.game.stream_music = not ctx.game.stream_music
        if ctx.game.stream_music:
            await ctx.send("Music stream enabled!")
        else:
            await ctx.send("Music stream disabled!")

    @tasks.loop(seconds=gamedata.TIMER_GAP)
    async def timer(self):
        """Timer loop for the bot"""

        for game in self.bot.games.values():
            # Skip server if game has not started
            if not game.started:
                continue
            # Skip server if game has ended
            if game.start_time + gamedata.GAME_LENGTH < time.time():
                continue

            remaining_time = (
                game.start_time + gamedata.GAME_LENGTH - time.time()
            )

            # Print timer message if enabled in a server
            if game.show_timer:
                text_channels = {
                    channel.name: channel
                    for channel in game.guild.text_channels
                }

                def pad(num):
                    return str(int(num)).zfill(2)

                await text_channels["bot-channel"].send((
                    f"{pad(remaining_time // 60)}:{pad(remaining_time % 60)}"
                ))

    @commands.command()
    async def search(self, ctx):
        """Draw a searching card"""

        if not ctx.game.started:
            await ctx.send("Game hasn't started yet!")
            return
        if not ctx.character:
            await ctx.send("You don't have a character role!")
            return

        search_card = random.choice(
            (filepaths.CARD_DIR / "Searching").glob("*.png")
        )
        asyncio.create_task(ctx.text_channels[f"{ctx.character}-clues"].send(
            file=discord.File(search_card)
        ))

    @commands.command(name="10")
    async def ten_min_card(
        self, ctx, character: typing.Union[discord.Member, discord.Role]
    ):
        """Assign the 10 minute card to another player"""

        if isinstance(character, discord.Member):
            if not ctx.character:
                await ctx.send("Could not find player!")
                return
            ctx.game.ten_char = ctx.character
        else:
            ctx.game.ten_char = ctx.character.name.lower()

    @commands.command()
    async def show_all(self, ctx):
        """Allows all members to read every channel and disables sending"""

        for channel in ctx.guild.text_channels:
            await channel.edit(sync_permissions=True)
        await ctx.send("All channels shown")


def setup(bot):
    bot.add_cog(Game(bot))
