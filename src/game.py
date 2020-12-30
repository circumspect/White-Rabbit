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

    @commands.command(aliases=["initialize"])
    async def init(self, ctx):
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
        alice = utils.POSTER_DIR / ("Alice Briarwood " + str(ctx.game.alice) + utils.IMAGE_EXT)
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
            "Explain motive cards", "Character backgrounds", "Relationships", 
            "Suspects and locations", "!setup_clues", "Explain clue cards", 
            "Explain searching", "Game guide", "Voicemails", 
            "Stream timer (https://www.youtube.com/watch?v=ysOOFIOAy7A)", 
            "!start", "Send first message", 
        ])
        prompts = utils.codeblock(prompts)

        background = " ".join([
            "CHARLIE BARNES moved away from Silent Falls", 
            "with their mom at the end of the last school year",
            "after their parents divorced. They just arrived in",
            "town to stay with their dad for winter break, and",
            "hope to see Alice and the others while they’re here.",
            "A few days ago, Alice stopped responding.", 
            "They haven’t heard from her since.",
        ])

        background = utils.codeblock(background)

        asyncio.create_task(channel.send(prompts))
        asyncio.create_task(channel.send(background))

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
        """Timer loop to check clues and perform various actions"""

        minutes_remaining = 90
        check_interval = 5

        while minutes_remaining > 0:
            if ctx.game.automatic:
                # Normal clue cards
                if minutes_remaining in gamedata.CLUE_TIMES and minutes_remaining <= ctx.game.next_clue:
                    self.bot.cogs["Manual"].send_clue(ctx, minutes_remaining)
                    if minutes_remaining == 30 and ctx.game.picked_clues[minutes_remaining] == 1:
                        flip = random.choice(["Heads", "Tails"])

                        for character in ctx.game.clue_assignments:
                            if 30 in ctx.game.clue_assignments[character]:
                                channel = character + "-clues"
                                break

                        channel = ctx.text_channels[channel]
                        asyncio.create_task(channel.send(flip))
                
                # If 20 minutes left, make check run every minute
                if minutes_remaining == 20:
                    check_interval = 1

                # Check if 10 min card has been assigned and send reminder if not
                if minutes_remaining == gamedata.TEN_MIN_REMINDER_TIME and not ctx.game.ten_char:
                    channel = ctx.text_channels["player-resources"]
                    asyncio.create_task(channel.send(gamedata.TEN_MIN_REMINDER_TEXT))

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

                # Ending 3
                elif minutes_remaining == 8 and ctx.game.second_culprit:
                    culprit = ctx.game.suspects_drawn[30]
                    
                    remaining_suspects = []
                    for suspect in gamedata.SUSPECTS:
                        if suspect != culprit:
                            remaining_suspects.append(suspect)
                    
                    second = random.choice(remaining_suspects)

                    # Send to clues channel
                    path = utils.SUSPECT_IMAGE_DIR / (gamedata.SUSPECTS[second] + ".png")
                    channel = ctx.game.ten_char + "-clues"
                    utils.send_image(channel, path, ctx)

                    # Send to suspects-drawn channel
                    channel = ctx.text_channels["suspects-drawn"]
                    asyncio.create_task(channel.send("SECOND CULPRIT:"))
                    utils.send_image(channel, path, ctx)

                # Endings 1 and 2
                elif minutes_remaining == 3 and ctx.game.three_flip:
                    flip = random.choice(["Heads", "Tails"])
                    channel = ctx.game.ten_char + "-clues"
                    channel = ctx.text_channels[channel]
                    asyncio.create_task(channel.send(flip))

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
                    await channel.send(f"Reminder: You have the {ctx.game.next_clue} minute clue card")

                # Wait out the rest of the interval
                await asyncio.sleep((check_interval - gamedata.REMINDER_BUFFER) * 60 / ctx.game.game_speed)

            minutes_remaining -= check_interval
        
        # End of game, send debrief
        utils.send_image(
            "charlie-clues",
            utils.MASTER_PATHS["debrief"],
            ctx
        )

    @commands.command(aliases=["searching"])
    async def search(self, ctx):
        """Draw a searching card"""

        if ctx.game.automatic and not ctx.game.start_time:
            await ctx.send("Game hasn't started yet!")
            return
        if not ctx.character:
            await ctx.send("You don't have a character role!")
            return

        search = random.choice(list(gamedata.SEARCHING))
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

        await ctx.send(f"Assigned 10 minute card to {character.title()}!")


def setup(bot):
    bot.add_cog(Game(bot))
