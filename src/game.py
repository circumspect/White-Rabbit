# Built-in
import asyncio
import datetime
import math
import random
import typing
# 3rd-party
import discord
from discord.ext import commands
# Local
import gamedata
import utils


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["init"])
    async def initialize(self, ctx):
        """Initial setup before character selection"""

        if ctx.game.start_time:
            await ctx.send("Game has already begun!")
            return
        elif ctx.game.init and ctx.game.automatic:
            # Disallow unless manual mode is enabled
            await ctx.send("Initialization already run!")
            return

        await ctx.send("Initializing game")

        # Introduction images
        utils.send_image(
            "player-resources",
            utils.MASTER_PATHS["guide"],
            ctx
        )
        utils.send_image(
            "player-resources",
            utils.MASTER_PATHS["character_sheet"],
            ctx
        )
        utils.send_image(
            "player-resources",
            utils.MASTER_PATHS["intro"],
            ctx
        )

        ctx.game.alice = random.randint(1, 10)
        alice = utils.POSTER_DIR / ("Alice Briarwood " + ctx.game.alice + utils.IMAGE_EXT)
        utils.send_image("player-resources", alice, ctx)

        # Send characters, suspects, and locations to appropriate channels
        utils.send_folder("character-cards", utils.CHARACTER_IMAGE_DIR, ctx)
        utils.send_folder("suspect-cards", utils.SUSPECT_IMAGE_DIR, ctx)
        utils.send_folder("location-cards", utils.LOCATION_IMAGE_DIR, ctx)

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
        for name in gamedata.CHARACTERS:
            channel = ctx.text_channels[f"{name}-clues"]
            utils.send_image(
                channel,
                utils.MASTER_PATHS[name],
                ctx
            )

        # Shuffle and send motives if in automatic mode
        if ctx.game.automatic:
            await self.bot.cogs["Manual"].shuffle_motives(ctx)
            asyncio.create_task(self.bot.cogs["Manual"].send_motives(ctx))

        ctx.game.init = True

    @commands.command()
    async def setup_clues(self, ctx):
        """Shuffle and distribute clues"""

        if (not ctx.game.init) and ctx.game.automatic:
            # Disallow if init hasn't been run yet and manual mode is off
            await ctx.send("Need to initialize first!")
            return
        elif ctx.game.start_time:
            await ctx.send("Game has already begun!")
            return

        player_count = len(ctx.game.char_roles())
        # Can't set up if there aren't enough players to assign clues
        if player_count < 3:
            await ctx.send("Not enough players!")
            return
        # Can't set up without Charlie Barnes
        elif "Charlie" not in ctx.game.char_roles():
            await ctx.send("Can't find Charlie!")
            return

        asyncio.create_task(ctx.send("Distributing clues!"))

        asyncio.create_task(self.bot.cogs["Manual"].shuffle_clues(ctx))
        asyncio.create_task(self.bot.cogs["Manual"].assign_clues(ctx))

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

        if ctx.game.start_time:
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
        await channel.send(file=discord.File(utils.CLUE_DIR / "90/90-1.png"))
        first_message = "Hey! Sorry for the big group text, but I just got "\
                        "into town for winter break at my dad's and haven't "\
                        "been able to get ahold of Alice. Just wondering if "\
                        "any of you have spoken to her?"
        await channel.send(first_message)

        if ctx.game.stream_music:
            if ctx.guild.voice_client is None:
                await ctx.guild.voice_channels[0].connect()
            ctx.guild.voice_client.play(
                discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                    utils.TIMER_AUDIO
                ))
            )

        ctx.game.start_time = datetime.datetime.now()
        asyncio.create_task(ctx.send("Starting the game!"))

        # Start timer and clue_check tasks simultaneously
        await (asyncio.gather(self.timer(ctx), self.clue_check(ctx)))

    async def timer(self, ctx):
        """Prints out the timer"""

        time_remaining = gamedata.GAME_LENGTH
        while time_remaining > 0:
            time_remaining -= ctx.game.timer_gap

            if ctx.game.show_timer:
                time = utils.time_string(time_remaining)
                await ctx.send(time)
            await asyncio.sleep(ctx.game.timer_gap / ctx.game.game_speed)

    async def clue_check(self, ctx):
        """Runs clue check every 5 minutes and calls send_clue()"""

        minutes_remaining = 90
        check_interval = 5

        while minutes_remaining > 0:
            # normal cards
            if ctx.game.automatic:
                if minutes_remaining in gamedata.CLUE_TIMES and minutes_remaining <= ctx.game.next_clue:
                    self.bot.cogs["Manual"].send_clue(ctx, minutes_remaining)

                # 10 min card
                elif minutes_remaining == 10:
                    channel = ctx.game.ten_char + "-clues"
                    ending = random.choice(list(i for i in ctx.game.endings if ctx.game.endings[i]))
                    clue = utils.CLUE_DIR / "10" / f"10-{ending}.png"
                    utils.send_image(channel, clue, ctx)

                    if ending != 3:
                        ctx.game.three_flip = True
                    else:
                        ctx.game.second_culprit = True

                    check_interval = 1

                # ending 3
                elif minutes_remaining == 8 and ctx.game.second_culprit:
                    culprit = ctx.game.suspects_drawn[30]
                    while culprit == ctx.game.suspects_drawn[30]:
                        culprit = random.choice(ctx.game.suspect_pile)
                    channel = ctx.text_channels["suspects-drawn"]
                    asyncio.create_task(channel.send("SECOND CULPRIT:"))
                    path = utils.SUSPECT_IMAGE_DIR / (gamedata.SUSPECTS[culprit] + ".png")
                    utils.send_image(channel, path, ctx)

                # endings 1 and 2
                elif minutes_remaining == 3 and ctx.game.three_flip:
                    flip = random.choice([True, False])
                    channel = ctx.game.ten_char + "-clues"
                    channel = ctx.text_channels[channel]
                    if flip:
                        asyncio.create_task(channel.send("Heads"))
                    else:
                        asyncio.create_task(channel.send("Tails"))

                await asyncio.sleep(check_interval * 60 / ctx.game.game_speed)

            # Manual
            else:
                # Wait for the buffer before sending the reminder
                await asyncio.sleep(gamedata.REMINDER_BUFFER * 60 / ctx.game.game_speed)

                # Check if player hasn't drawn the clue yet
                if minutes_remaining <= ctx.game.next_clue:
                    # Find character who owns the clue
                    for name in ctx.game.clue_assignments:
                        if minutes_remaining in ctx.game.clue_assignments[name]:
                            character = name
                            break

                    channel = ctx.text_channels[character + "-clues"]
                    await channel.send(f"Reminder: You have the {minutes_remaining} minute clue card")

                # Wait out the rest of the interval
                await asyncio.sleep((check_interval - gamedata.REMINDER_BUFFER) * 60 / ctx.game.game_speed)

            minutes_remaining -= check_interval

    @commands.command()
    async def search(self, ctx):
        """Draw a searching card"""

        if not ctx.game.start_time:
            await ctx.send("Game hasn't started yet!")
            return
        if not ctx.character:
            await ctx.send("You don't have a character role!")
            return

        search = random.choice(list(gamedata.SEARCHING))
        print(ctx.character)
        ctx.game.searches[ctx.character].append(search)
        image = utils.SEARCHING_DIR / (gamedata.SEARCHING[search] + utils.IMAGE_EXT)
        asyncio.create_task(ctx.text_channels[f"{ctx.character}-clues"].send(
            file=discord.File(image)
        ))

    @commands.command(name="10")
    async def ten_min_card(
        self, ctx, mention: typing.Union[discord.Member, discord.Role]
    ):
        """Assign the 10 minute card to another player"""

        if isinstance(mention, discord.Member):
            character = mention.nick.split()[0].lower()
        else:
            character = mention.name.lower()

        ctx.game.ten_char = character

    @commands.command()
    async def show_all(self, ctx):
        """Allows all members to read every channel and disables sending"""

        for channel in ctx.guild.text_channels:
            await channel.edit(sync_permissions=True)
        await ctx.send("All channels shown")


def setup(bot):
    bot.add_cog(Game(bot))
