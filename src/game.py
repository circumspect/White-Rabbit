# Built-in
import asyncio
import datetime
import random
import typing
# 3rd-party
import discord
from discord.ext import commands
# Local
import gamedata
import utils
from localization import LOCALIZATION_DATA

loc = LOCALIZATION_DATA["commands"]["game"]


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name=loc["init"]["name"],
        aliases=loc["init"]["aliases"],
        description=loc["init"]["description"]
    )
    async def init(self, ctx):
        """Initial setup before character selection"""

        if ctx.game.start_time:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["AlreadyStarted"]))
            return
        elif ctx.game.init and ctx.game.automatic:
            # Disallow another initialization attempt unless manual mode is enabled
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["AlreadyInitialized"]))
            return

        asyncio.create_task(ctx.send(LOCALIZATION_DATA["messages"]["Initializing"]))

        # Introduction images
        utils.send_image(
            LOCALIZATION_DATA["channels"]["resources"],
            utils.MASTER_PATHS["guide"],
            ctx
        )
        utils.send_image(
            LOCALIZATION_DATA["channels"]["resources"],
            utils.MASTER_PATHS["intro"],
            ctx
        )

        if ctx.game.automatic:
            asyncio.create_task(self.bot.cogs["Manual"].alice(ctx))

        # Send characters, suspects, and locations to appropriate channels
        utils.send_folder(
            LOCALIZATION_DATA["channels"]["cards"]["character-cards"], utils.CHARACTER_IMAGE_DIR, ctx
        )
        utils.send_folder(
            LOCALIZATION_DATA["channels"]["cards"]["suspect-cards"], utils.SUSPECT_IMAGE_DIR, ctx
        )
        utils.send_folder(
            LOCALIZATION_DATA["channels"]["cards"]["location-cards"], utils.LOCATION_IMAGE_DIR, ctx
        )

        # Instructions for Charlie Barnes
        channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["clues"]["charlie"]]
        prompts = "\n".join(LOCALIZATION_DATA["stuff-for-charlie"]["instructions"])
        prompts = utils.codeblock(prompts)

        background = LOCALIZATION_DATA["stuff-for-charlie"]["background"]

        background = utils.codeblock(background)

        asyncio.create_task(channel.send(prompts))
        asyncio.create_task(channel.send(background))

        # Character and motive cards in clues channels
        for name in gamedata.CHARACTERS:
            channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["clues"][name]]
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

    @commands.command(
        name=loc["setup_clues"]["name"],
        aliases=loc["setup_clues"]["aliases"],
        description=loc["setup_clues"]["description"]
    )
    async def setup_clues(self, ctx):
        """Shuffle and distribute clues"""

        if (not ctx.game.init) and ctx.game.automatic:
            # Disallow if init hasn't been run yet and manual mode is off
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["NotInitialized"]))
            return
        elif ctx.game.start_time:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["AlreadyStarted"]))
            return

        player_count = len(ctx.game.char_roles())
        # Can't set up if there aren't enough players to assign clues
        if player_count < 3:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["NotEnoughPlayers"]))
            return
        # Can't set up without Charlie Barnes
        elif "Charlie" not in ctx.game.char_roles():
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["MissingCharlie"]))
            return

        asyncio.create_task(ctx.send(LOCALIZATION_DATA["messages"]["DistributingClues"]))

        asyncio.create_task(self.bot.cogs["Manual"].shuffle_clues(ctx))
        asyncio.create_task(self.bot.cogs["Manual"].assign_times(ctx))
        asyncio.create_task(self.bot.cogs["Manual"].print_times(ctx))

        ctx.game.setup = True

    @commands.command(
        name=loc["example"]["name"],
        aliases=loc["example"]["aliases"],
        description=loc["example"]["description"]
    )
    async def example(self, ctx):
        """Sends an example clue and suspect"""

        # Send random 80 minute clue card
        channel = LOCALIZATION_DATA["channels"]["resources"]
        choice = random.randint(1, 3)
        path = utils.get_image(utils.CLUE_DIR / "80", f"80-{choice}")
        utils.send_image(channel, path, ctx)

        # Send suspect card
        suspect = random.choice(list(gamedata.SUSPECTS.keys()))
        path = utils.MASTER_PATHS[suspect]
        utils.send_image(channel, path, ctx)

    @commands.command(
        name=loc["char_sheet"]["name"],
        aliases=loc["char_sheet"]["aliases"],
        description=loc["char_sheet"]["description"]
    )
    async def char_sheet(self, ctx):
        """Sends the character sheet to the resources channel"""

        utils.send_image(
            LOCALIZATION_DATA["channels"]["resources"],
            utils.MASTER_PATHS["character_sheet"],
            ctx
        )

    @commands.command(
        name=loc["start"]["name"],
        aliases=loc["start"]["aliases"],
        description=loc["start"]["description"]
    )
    async def start(self, ctx):
        """Begins the game"""

        # Validity checks
        if not ctx.game.alice:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["MissingAlice"]))
            return

        if not ctx.game.setup:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["NeedToSetUp"]))
            return

        if ctx.game.start_time:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["AlreadyStarted"]))
            return

        if "Charlie" not in ctx.game.char_roles():
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["MissingCharlie"]))
            return

        if len(ctx.game.char_roles()) < 3:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["NotEnoughPlayers"]))
            return

        # 90 minute card/message for Charlie Barnes
        channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["clues"]["charlie"]]
        await channel.send(file=discord.File(utils.get_image(utils.CLUE_DIR / "90", "90-1")))
        first_message = LOCALIZATION_DATA["stuff-for-charlie"]["first-message"]
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
        asyncio.create_task(ctx.send(LOCALIZATION_DATA["messages"]["StartingGame"]))

        # Start timer and clue_check tasks simultaneously
        await asyncio.gather(self.timer(ctx), self.clue_check(ctx))

    async def timer(self, ctx):
        """Prints out the timer"""

        time_remaining = gamedata.GAME_LENGTH
        while time_remaining > 0:
            time_remaining -= ctx.game.timer_gap

            if ctx.game.show_timer:
                time = utils.time_string(time_remaining)
                asyncio.create_task(ctx.send(time))
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
                        flip = utils.flip()

                        for character in ctx.game.clue_assignments:
                            if 30 in ctx.game.clue_assignments[character]:
                                channel = LOCALIZATION_DATA["channels"]["clues"][character]
                                break

                        channel = ctx.text_channels[channel]
                        asyncio.create_task(channel.send(flip))

                # If 20 minutes left, make check run every minute
                if minutes_remaining == 20:
                    check_interval = 1

                # Check if 10 min card has been assigned and send reminder if not
                if minutes_remaining == gamedata.TEN_MIN_REMINDER_TIME and not ctx.game.ten_char:
                    channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["resources"]]
                    asyncio.create_task(channel.send("@everyone " + gamedata.TEN_MIN_REMINDER_TEXT))

                # 10 min card
                elif minutes_remaining == 10:
                    # If not assigned, default to Charlie
                    if not ctx.game.ten_char:
                        ctx.game.ten_char = "charlie"

                    channel = LOCALIZATION_DATA["channels"]["clues"][ctx.game.ten_char]
                    ending = random.choice(list(i for i in ctx.game.endings if ctx.game.endings[i]))
                    clue = utils.get_image(utils.CLUE_DIR / "10", f"10-{ending}")
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
                    path = utils.get_image(utils.SUSPECT_IMAGE_DIR, gamedata.SUSPECTS[second])
                    channel = LOCALIZATION_DATA["channels"]["clues"][ctx.game.ten_char]
                    utils.send_image(channel, path, ctx)

                    # Send to suspects-drawn channel
                    channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["cards"]["suspects-drawn"]]
                    asyncio.create_task(channel.send(LOCALIZATION_DATA["messages"]["SecondCulprit"]))
                    utils.send_image(channel, path, ctx)

                # Endings 1 and 2
                elif minutes_remaining == 3 and ctx.game.three_flip:
                    flip = utils.flip()
                    channel = LOCALIZATION_DATA["channels"]["clues"][ctx.game.ten_char]
                    channel = ctx.text_channels[channel]
                    asyncio.create_task(channel.send(flip))

                await asyncio.sleep(check_interval * 60 / ctx.game.game_speed)

            # Manual mode
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

                    channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["clues"][character]]
                    message = LOCALIZATION_DATA["messages"]["NextClueReminder"]
                    asyncio.create_task(channel.send(f"{message} ({ctx.game.next_clue})"))

                # Wait out the rest of the interval
                await asyncio.sleep((check_interval - gamedata.REMINDER_BUFFER) * 60 / ctx.game.game_speed)

            minutes_remaining -= check_interval

        # End of game, send debrief
        utils.send_image(
            LOCALIZATION_DATA["channels"]["clues"]["charlie"],
            utils.MASTER_PATHS["debrief"],
            ctx
        )

    @commands.command(
        name=loc["search"]["name"],
        aliases=loc["search"]["aliases"],
        description=loc["search"]["description"]
    )
    async def search(self, ctx):
        """Draw a searching card"""

        if ctx.game.automatic and not ctx.game.start_time:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["GameNotStarted"]))
            return
        if not ctx.character:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["NotACharacter"]))
            return

        char_channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["clues"][ctx.character]]

        if ctx.game.search_cards:
            search = random.choice(ctx.game.search_cards)
            ctx.game.search_cards.remove(search)
            image = utils.get_image(utils.SEARCHING_DIR, search)
            asyncio.create_task(char_channel.send(file=discord.File(image)))

        else:
            # out of unique cards
            asyncio.create_task(char_channel.send(loc["search"]["NothingFound"]))

    @commands.command(
        name=loc["ten_min_card"]["name"],
        aliases=loc["ten_min_card"]["aliases"],
        description=loc["ten_min_card"]["description"]
    )
    async def ten_min_card(
        self, ctx, mention: typing.Union[discord.Member, discord.Role]
    ):
        """Assign the 10 minute card to another player"""

        if isinstance(mention, discord.Member):
            character = mention.nick.split()[0]
        else:
            character = mention.name

        if character.title() not in ctx.game.char_roles():
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["PlayerNotFound"]))
            return

        ctx.game.ten_char = character.lower()

        asyncio.create_task(ctx.send(loc["ten_min_card"]["Assigned"]))


def setup(bot):
    bot.add_cog(Game(bot))
