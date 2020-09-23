# Built-in
import asyncio
import math
import random
import time
import typing
# 3rd-party
import discord
from discord.ext import commands, tasks
# Local
import utils
import gamedata


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["init"])
    async def initialize(self, ctx):
        """Initial setup before character selection"""

        if ctx.game.started:
            await ctx.send("Game has already begun!")
            return
        elif ctx.game.init:
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
        alice = random.choice(list(
            (utils.POSTER_DIR).glob("*.png")
        ))
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
    async def setup(self, ctx):
        """Setup after players have chosen characters"""
        
        if not ctx.game.init:
            await ctx.send("Need to initialize first!")
            return
        elif ctx.game.started:
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
        
        asyncio.create_task(ctx.send("Finishing setup!"))

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

        ctx.game.started = True
        asyncio.create_task(ctx.send("Starting the game!"))

        # Start timer and clue_check tasks simultaneously
        await (asyncio.gather(self.timer(ctx), self.clue_check(ctx)))
    
    async def timer(self, ctx):
        """Prints out the timer"""

        def pad(num):
            return str(int(num)).zfill(2)
        
        time_remaining = gamedata.GAME_LENGTH
        while time_remaining > 0:
            time_remaining -= gamedata.TIMER_GAP

            minutes = math.floor(time_remaining / 60)
            seconds =  time_remaining % 60
            if ctx.game.show_timer:
                await ctx.send(":".join((pad(minutes), pad(seconds))))
            await asyncio.sleep(gamedata.TIMER_GAP)

    async def clue_check(self, ctx):
        """Runs clue check every 5 minutes and calls send_clue()"""
        
        minutes_remaining = 90
        check_interval = 5
        while minutes_remaining > 0:
            if ctx.game.automatic:
                if minutes_remaining in gamedata.CLUE_TIMES and minutes_remaining <= ctx.game.next_clue:
                    self.bot.cogs["Manual"].send_clue(ctx.game, minutes_remaining)
                await asyncio.sleep(check_interval * 60)
            else:
                # Wait for the buffer before sending the reminder
                await asyncio.sleep(gamedata.REMINDER_BUFFER * 60)
                
                # Check if player hasn't drawn the clue yet
                if minutes_remaining <= ctx.game.next_clue:
                    # Find character who owns the clue
                    for name in ctx.game.clue_assignments:
                        if time in ctx.game.clue_assignments[name]:
                            character = name
                            break
                    
                    channel = ctx.text_channels[character + "-clues"]
                    await channel.send("Reminder: You have the " + str(minutes_remaining) + " minute clue card")

                # Wait out the rest of the interval
                await asyncio.sleep((check_interval - gamedata.REMINDER_BUFFER) * 60)
            minutes_remaining -= check_interval

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
            list((utils.CARD_DIR / "Searching").glob("*.png"))
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
