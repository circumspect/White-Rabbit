# pylint: disable=unsubscriptable-object   # https://github.com/PyCQA/pylint/issues/3637#issuecomment-720097674

# Built-in
import asyncio
import datetime
import random
import typing

import lightbulb
from lightbulb import commands
from utils.localization import LOCALIZATION_DATA
from utils import dirs, filepaths, gamedata, miscutils

plugin = lightbulb.Plugin("Game")
loc = LOCALIZATION_DATA["commands"]["game"]


@plugin.command()
@lightbulb.command(
    loc["init"]["name"], loc["init"]["description"], aliases=loc["init"]["aliases"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def init(ctx: lightbulb.Context) -> None:
    """Initial setup before character selection"""
    game = ctx.bot.d.games[ctx.guild_id]
    if game.start_time:
        await ctx.respond(LOCALIZATION_DATA["errors"]["AlreadyStarted"])
        return
    elif game.init and game.automatic:
        # Disallow another initialization attempt unless manual mode is enabled
        await ctx.respond(LOCALIZATION_DATA["errors"]["AlreadyInitialized"])
        return

    await ctx.respond(LOCALIZATION_DATA["messages"]["Initializing"])

    # Introduction images
    miscutils.send_image(
        LOCALIZATION_DATA["channels"]["resources"],
        filepaths.MASTER_PATHS["guide"],
        ctx.get_guild(),
    )
    miscutils.send_image(
        LOCALIZATION_DATA["channels"]["resources"],
        filepaths.MASTER_PATHS["intro"],
        ctx.get_guild(),
    )

    if ctx.game.automatic:
        asyncio.create_task(ctx.bot.cogs["Manual"].alice(ctx))

    # Send characters, suspects, and locations to appropriate channels
    for character in sorted(gamedata.CHARACTERS.keys()):
        filepath = miscutils.get_image(dirs.CHARACTER_INTRODUCTIONS_DIR, character)
        miscutils.send_image(
            LOCALIZATION_DATA["channels"]["cards"]["character-cards"],
            filepath,
            ctx.get_guild(),
        )
    for suspect in sorted(gamedata.SUSPECTS.keys()):
        filepath = miscutils.get_image(dirs.SUSPECT_IMAGE_DIR, suspect)
        miscutils.send_image(
            LOCALIZATION_DATA["channels"]["cards"]["suspect-cards"],
            filepath,
            ctx.get_guild(),
        )
    for location in sorted(gamedata.LOCATIONS.keys()):
        filepath = miscutils.get_image(dirs.LOCATION_IMAGE_DIR, location)
        miscutils.send_image(
            LOCALIZATION_DATA["channels"]["cards"]["location-cards"],
            filepath,
            ctx.get_guild(),
        )

    # Instructions for Charlie Barnes
    channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["clues"]["charlie"]]
    prompts = "\n".join(LOCALIZATION_DATA["stuff-for-charlie"]["instructions"])
    prompts = miscutils.codeblock(prompts)

    background = LOCALIZATION_DATA["stuff-for-charlie"]["background"]

    background = miscutils.codeblock(background)

    asyncio.create_task(channel.send(prompts))
    asyncio.create_task(channel.send(background))

    # Character and motive cards in clues channels
    for name in gamedata.CHARACTERS:
        channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["clues"][name]]
        miscutils.send_image(channel, filepaths.MASTER_PATHS[name], ctx.get_guild())

    # Shuffle and send motives if in automatic mode
    if ctx.game.automatic:
        await ctx.bot.cogs["Manual"].shuffle_motives(ctx)
        asyncio.create_task(ctx.bot.cogs["Manual"].send_motives(ctx))

    ctx.game.init = True


@plugin.command()
@lightbulb.command(
    loc["setup_clues"]["name"],
    loc["setup_clues"]["description"],
    aliases=loc["setup_clues"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def setup_clues(ctx: lightbulb.Context) -> None:
    """Shuffle and distribute clues"""

    if (not ctx.game.init) and ctx.game.automatic:
        # Disallow if init hasn't been run yet and manual mode is off
        asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["NotInitialized"]))
        return
    elif ctx.game.start_time:
        asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["AlreadyStarted"]))
        return

    player_count = len(ctx.game.char_roles())
    # Can't set up if there aren't enough players to assign clues
    if player_count < 3:
        asyncio.create_task(
            ctx.respond(LOCALIZATION_DATA["errors"]["NotEnoughPlayers"])
        )
        return
    # Can't set up without Charlie Barnes
    elif "Charlie" not in ctx.game.char_roles():
        asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["MissingCharlie"]))
        return

    asyncio.create_task(ctx.respond(LOCALIZATION_DATA["messages"]["DistributingClues"]))

    asyncio.create_task(ctx.bot.cogs["Manual"].shuffle_clues(ctx))
    asyncio.create_task(ctx.bot.cogs["Manual"].assign_times(ctx))
    asyncio.create_task(ctx.bot.cogs["Manual"].print_times(ctx))

    ctx.game.setup = True


@plugin.command()
@lightbulb.command(
    loc["example"]["name"],
    loc["example"]["description"],
    aliases=loc["example"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def example(ctx: lightbulb.Context) -> None:
    """Sends an example clue and suspect"""

    # Send random 80 minute clue card
    channel = LOCALIZATION_DATA["channels"]["resources"]
    choice = random.randint(1, 3)
    path = miscutils.get_image(dirs.CLUE_DIR / "80", f"80-{choice}")
    miscutils.send_image(channel, path, ctx.get_guild())

    # Send suspect card
    suspect = random.choice(list(gamedata.SUSPECTS.keys()))
    path = filepaths.MASTER_PATHS[suspect]
    miscutils.send_image(channel, path, ctx.get_guild())


@plugin.command()
@lightbulb.command(
    loc["char_sheet"]["name"],
    loc["char_sheet"]["description"],
    aliases=loc["char_sheet"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def char_sheet(ctx: lightbulb.Context) -> None:
    """Sends the character sheet to the resources channel"""

    miscutils.send_image(
        LOCALIZATION_DATA["channels"]["resources"],
        filepaths.MASTER_PATHS["character_sheet"],
        ctx.get_guild(),
    )


@plugin.command()
@lightbulb.command(
    loc["start"]["name"], loc["start"]["description"], aliases=loc["start"]["aliases"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def start(ctx: lightbulb.Context) -> None:
    """Begins the game"""

    # Validity checks
    if not ctx.game.alice:
        asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["MissingAlice"]))
        return

    if not ctx.game.setup:
        asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["NeedToSetUp"]))
        return

    if ctx.game.start_time:
        asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["AlreadyStarted"]))
        return

    if "Charlie" not in ctx.game.char_roles():
        asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["MissingCharlie"]))
        return

    if len(ctx.game.char_roles()) < 3:
        asyncio.create_task(
            ctx.respond(LOCALIZATION_DATA["errors"]["NotEnoughPlayers"])
        )
        return

    # 90 minute card/message for Charlie Barnes
    channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["clues"]["charlie"]]
    miscutils.send_image(
        channel, miscutils.get_image(dirs.CLUE_DIR / "90", "90-1"), ctx.get_guild()
    )
    first_message = LOCALIZATION_DATA["stuff-for-charlie"]["first-message"]
    await channel.send(first_message)

    if ctx.game.stream_music:
        pass

    ctx.game.start_time = datetime.datetime.now()
    asyncio.create_task(ctx.respond(LOCALIZATION_DATA["messages"]["StartingGame"]))

    # Start timer and clue_check tasks simultaneously
    await asyncio.gather(timer(ctx), clue_check(ctx))


async def timer(self, ctx):
    """Prints out the timer"""

    time_remaining = gamedata.GAME_LENGTH
    while time_remaining > 0:
        time_remaining -= ctx.game.timer_gap

        if ctx.game.show_timer:
            time = miscutils.time_string(time_remaining)
            asyncio.create_task(ctx.respond(time))
        await asyncio.sleep(ctx.game.timer_gap / ctx.game.game_speed)


async def clue_check(self, ctx):
    """Timer loop to check clues and perform various actions"""

    minutes_remaining = 90
    check_interval = 5

    while minutes_remaining > 0:
        if ctx.game.automatic:
            # Normal clue cards
            if (
                minutes_remaining in gamedata.CLUE_TIMES
                and minutes_remaining <= ctx.game.next_clue
            ):
                self.bot.cogs["Manual"].send_clue(ctx, minutes_remaining)
                if (
                    minutes_remaining == 30
                    and ctx.game.picked_clues[minutes_remaining] == 1
                ):
                    flip = miscutils.flip()

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
            if (
                minutes_remaining == gamedata.TEN_MIN_REMINDER_TIME
                and not ctx.game.ten_char
            ):
                channel = ctx.text_channels[LOCALIZATION_DATA["channels"]["resources"]]
                asyncio.create_task(
                    channel.send("@everyone " + gamedata.TEN_MIN_REMINDER_TEXT)
                )

            # 10 min card
            elif minutes_remaining == 10:
                # If not assigned, default to Charlie
                if not ctx.game.ten_char:
                    ctx.game.ten_char = "charlie"

                channel = LOCALIZATION_DATA["channels"]["clues"][ctx.game.ten_char]
                ending = random.choice(
                    [i for i in ctx.game.endings if ctx.game.endings[i]]
                )
                clue = miscutils.get_image(dirs.CLUE_DIR / "10", f"10-{ending}")
                miscutils.send_image(channel, clue, ctx.get_guild())

                if ending != 3:
                    ctx.game.three_flip = True
                else:
                    ctx.game.second_culprit = True

            # Ending 3
            elif minutes_remaining == 8 and ctx.game.second_culprit:
                culprit = ctx.game.suspects_drawn[30]
                remaining_suspects = [
                    suspect for suspect in gamedata.SUSPECTS if suspect != culprit
                ]
                second = random.choice(remaining_suspects)

                # Send to clues channel
                path = miscutils.get_image(dirs.SUSPECT_IMAGE_DIR, second)
                channel = LOCALIZATION_DATA["channels"]["clues"][ctx.game.ten_char]
                miscutils.send_image(channel, path, ctx.get_guild())

                # Send to suspects-drawn channel
                channel = ctx.text_channels[
                    LOCALIZATION_DATA["channels"]["cards"]["suspects-drawn"]
                ]
                asyncio.create_task(
                    channel.send(LOCALIZATION_DATA["messages"]["SecondCulprit"])
                )
                miscutils.send_image(channel, path,  ctx.get_guild())

            # Endings 1 and 2
            elif minutes_remaining == 3 and ctx.game.three_flip:
                flip = miscutils.flip()
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

                channel = ctx.text_channels[
                    LOCALIZATION_DATA["channels"]["clues"][character]
                ]
                message = LOCALIZATION_DATA["messages"]["NextClueReminder"]
                asyncio.create_task(channel.send(f"{message} ({ctx.game.next_clue})"))

            # Wait out the rest of the interval
            await asyncio.sleep(
                (check_interval - gamedata.REMINDER_BUFFER) * 60 / ctx.game.game_speed
            )

        minutes_remaining -= check_interval

    # End of game, send debrief
    miscutils.send_image(
        LOCALIZATION_DATA["channels"]["clues"]["charlie"],
        filepaths.MASTER_PATHS["debrief"],
         ctx.get_guild(),
    )


@plugin.command()
@lightbulb.command(
    loc["search"]["name"],
    loc["search"]["description"],
    aliases=loc["search"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def search(ctx: lightbulb.Context) -> None:
    """Draw a searching card"""

    if ctx.game.automatic and not ctx.game.start_time:
        asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["GameNotStarted"]))
        return
    if not ctx.character:
        asyncio.create_task(
            ctx.respond(LOCALIZATION_DATA["errors"]["NoCharacterRoles"])
        )
        return

    char_channel = ctx.text_channels[
        LOCALIZATION_DATA["channels"]["clues"][ctx.character]
    ]

    if ctx.game.search_cards:
        search = random.choice(ctx.game.search_cards)
        ctx.game.search_cards.remove(search)
        image = miscutils.get_image(dirs.SEARCHING_DIR, search)
        miscutils.send_image(char_channel, image, ctx.get_guild())

    else:
        # out of unique cards
        asyncio.create_task(char_channel.send(loc["search"]["NothingFound"]))


@plugin.command()
@lightbulb.command(
    loc["ten_min_card"]["name"],
    loc["ten_min_card"]["description"],
    aliases=loc["ten_min_card"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def ten_min_card(ctx: lightbulb.Context) -> None:
    """Assign the 10 minute card to another player"""
    mention = None
    if isinstance(mention, hikari.Member):
        character = mention.nick.split()[0]
    else:
        character = mention.name

    if character.title() not in ctx.game.char_roles():
        asyncio.create_task(ctx.respond(LOCALIZATION_DATA["errors"]["PlayerNotFound"]))
        return

    ctx.game.ten_char = character.lower()

    asyncio.create_task(ctx.respond(loc["ten_min_card"]["Assigned"]))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
