# pylint: disable=unsubscriptable-object   # https://github.com/PyCQA/pylint/issues/3637#issuecomment-720097674

# Built-in
import asyncio
import datetime
import random

import lightbulb
import hikari
from utils.localization import LOCALIZATION_DATA
from utils import dirs, gamedata, miscutils, errors

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
        raise errors.GameAlreadyStarted()
    elif game.init and game.automatic:
        # Disallow another initialization attempt unless manual mode is enabled
        raise errors.GameAlreadyInitialized()

    await ctx.respond(LOCALIZATION_DATA["messages"]["Initializing"])

    # Introduction images
    miscutils.send_image(
        LOCALIZATION_DATA["channels"]["resources"],
        gamedata.MASTER_PATHS["guide"],
        ctx.get_guild(),
    )
    miscutils.send_image(
        LOCALIZATION_DATA["channels"]["resources"],
        gamedata.MASTER_PATHS["intro"],
        ctx.get_guild(),
    )

    if game.automatic:
        game.alice = random.randint(1, 10)
        await game.send_alice()

    # Send characters, suspects, and locations to appropriate channels
    for character in sorted(gamedata.CHARACTERS.keys()):
        filepath = miscutils.get_image(dirs.CHARACTER_INTRODUCTIONS_DIR, character)
        miscutils.send_image(
            LOCALIZATION_DATA["channels"]["cards"]["character-cards"],
            filepath,
            game.guild,
        )
    for suspect in sorted(gamedata.SUSPECTS.keys()):
        filepath = miscutils.get_image(dirs.SUSPECT_IMAGE_DIR, suspect)
        miscutils.send_image(
            LOCALIZATION_DATA["channels"]["cards"]["suspect-cards"],
            filepath,
            game.guild,
        )
    for location in sorted(gamedata.LOCATIONS.keys()):
        filepath = miscutils.get_image(dirs.LOCATION_IMAGE_DIR, location)
        miscutils.send_image(
            LOCALIZATION_DATA["channels"]["cards"]["location-cards"],
            filepath,
            game.guild,
        )
    text_channels = miscutils.get_text_channels(game.guild)
    # Instructions for Charlie Barnes
    channel = text_channels[LOCALIZATION_DATA["channels"]["clues"]["charlie"]]
    prompts = "\n".join(LOCALIZATION_DATA["stuff-for-charlie"]["instructions"])
    prompts = miscutils.codeblock(prompts)

    background = LOCALIZATION_DATA["stuff-for-charlie"]["background"]

    background = miscutils.codeblock(background)

    await channel.send(background)
    await channel.send(prompts)

    # Character and motive cards in clues channels
    for name in gamedata.CHARACTERS:
        channel = text_channels[LOCALIZATION_DATA["channels"]["clues"][name]]
        miscutils.send_image(channel, gamedata.MASTER_PATHS[name], ctx.get_guild())

    # Shuffle and send motives if in automatic mode
    if game.automatic:
        game.shuffle_motives()
        await game.send_motives()

    game.init = True


@plugin.command()
@lightbulb.command(
    loc["setup_clues"]["name"],
    loc["setup_clues"]["description"],
    aliases=loc["setup_clues"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def setup_clues(ctx: lightbulb.Context) -> None:
    """Shuffle and distribute clues"""
    game = ctx.bot.d.games[ctx.guild_id]
    if (not game.init) and game.automatic:
        # Disallow if init hasn't been run yet and manual mode is off
        await ctx.respond(LOCALIZATION_DATA["errors"]["NotInitialized"])
        return
    elif game.start_time:
        raise errors.GameAlreadyStarted()

    await ctx.respond(LOCALIZATION_DATA["messages"]["DistributingClues"])

    game.shuffle_clues()
    game.assign_clues()
    await game.send_times()

    game.setup = True


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
    path = gamedata.MASTER_PATHS[suspect]
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
        gamedata.MASTER_PATHS["character_sheet"],
        ctx.get_guild(),
    )


@plugin.command()
@lightbulb.command(
    loc["start"]["name"], loc["start"]["description"], aliases=loc["start"]["aliases"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def start(ctx: lightbulb.Context) -> None:
    """Begins the game"""
    game = ctx.bot.d.games[ctx.guild_id]
    # Validity checks
    if not game.alice:
        await ctx.respond(LOCALIZATION_DATA["errors"]["MissingAlice"])
        return

    if not game.setup:
        await ctx.respond(LOCALIZATION_DATA["errors"]["NeedToSetUp"])
        return

    if game.start_time:
        raise errors.GameAlreadyStarted()

    if "Charlie" not in game.char_roles():
        raise errors.MissingCharlie()

    if len(game.char_roles()) < 3:
        raise errors.NotEnoughPlayers()

    # 90 minute card/message for Charlie Barnes
    channel = miscutils.get_text_channels(game.guild)[
        LOCALIZATION_DATA["channels"]["clues"]["charlie"]
    ]
    miscutils.send_image(
        channel, miscutils.get_image(dirs.CLUE_DIR / "90", "90-1"), game.guild
    )
    first_message = LOCALIZATION_DATA["stuff-for-charlie"]["first-message"]
    await channel.send(first_message)

    game.start_time = datetime.datetime.now()
    await ctx.respond(LOCALIZATION_DATA["messages"]["StartingGame"])

    # Start timer and clue_check tasks simultaneously
    await asyncio.gather(timer(ctx), clue_check(game))


async def timer(ctx):
    """Prints out the timer"""
    game = ctx.bot.d.games[ctx.guild_id]
    time_remaining = gamedata.GAME_LENGTH
    while time_remaining > 0:
        time_remaining -= game.timer_gap

        if game.show_timer:
            time = miscutils.time_string(time_remaining)
            await ctx.respond(time)
        await asyncio.sleep(game.timer_gap / game.game_speed)


async def clue_check(game):
    """Timer loop to check clues and perform various actions"""
    text_channels = miscutils.get_text_channels(game.guild)
    minutes_remaining = 90
    check_interval = 5

    while minutes_remaining > 0:
        if game.automatic:
            # Normal clue cards
            if (
                minutes_remaining in gamedata.CLUE_TIMES
                and minutes_remaining <= game.next_clue
            ):
                await game.send_clue(minutes_remaining)
                if (
                    minutes_remaining == 30
                    and game.picked_clues[minutes_remaining] == 1
                ):
                    flip = miscutils.flip()

                    for character in game.clue_assignments:
                        if 30 in game.clue_assignments[character]:
                            channel = LOCALIZATION_DATA["channels"]["clues"][character]
                            break

                    channel = text_channels[channel]
                    await channel.send(flip)

            # If 20 minutes left, make check run every minute
            if minutes_remaining == 20:
                check_interval = 1

            # Check if 10 min card has been assigned and send reminder if not
            if (
                minutes_remaining == gamedata.TEN_MIN_REMINDER_TIME
                and not game.ten_char
            ):
                channel = text_channels[LOCALIZATION_DATA["channels"]["resources"]]
                await channel.send(
                    "@everyone " + gamedata.TEN_MIN_REMINDER_TEXT,
                    mentions_everyone=True,
                )

            # 10 min card
            elif minutes_remaining == 10:
                # If not assigned, default to Charlie
                if not game.ten_char:
                    game.ten_char = "charlie"

                channel = LOCALIZATION_DATA["channels"]["clues"][game.ten_char]
                ending = random.choice([i for i in game.endings if game.endings[i]])
                clue = miscutils.get_image(dirs.CLUE_DIR / "10", f"10-{ending}")
                miscutils.send_image(channel, clue, game.guild)

                if ending != 3:
                    game.three_flip = True
                else:
                    game.second_culprit = True

            # Ending 3
            elif minutes_remaining == 8 and game.second_culprit:
                culprit = game.suspects_drawn[30]
                remaining_suspects = [
                    suspect for suspect in gamedata.SUSPECTS if suspect != culprit
                ]
                second = random.choice(remaining_suspects)

                # Send to clues channel
                path = miscutils.get_image(dirs.SUSPECT_IMAGE_DIR, second)
                channel = LOCALIZATION_DATA["channels"]["clues"][game.ten_char]
                miscutils.send_image(channel, path, game.guild)

                # Send to suspects-drawn channel
                channel = text_channels[
                    LOCALIZATION_DATA["channels"]["cards"]["suspects-drawn"]
                ]
                await channel.send(LOCALIZATION_DATA["messages"]["SecondCulprit"])
                miscutils.send_image(channel, path, game.guild)

            # Endings 1 and 2
            elif minutes_remaining == 3 and game.three_flip:
                flip = miscutils.flip()
                channel = text_channels[
                    LOCALIZATION_DATA["channels"]["clues"][game.ten_char]
                ]
                await channel.send(flip)

            await asyncio.sleep(check_interval * 60 / game.game_speed)

        # Manual mode
        else:
            # Wait for the buffer before sending the reminder
            await asyncio.sleep(gamedata.REMINDER_BUFFER * 60 / game.game_speed)

            # Check if player hasn't drawn the clue yet
            if minutes_remaining <= game.next_clue:
                # Find character who owns the clue
                for name in game.clue_assignments:
                    if game.next_clue in game.clue_assignments[name]:
                        character = name
                        break

                channel = text_channels[
                    LOCALIZATION_DATA["channels"]["clues"][character]
                ]
                message = LOCALIZATION_DATA["messages"]["NextClueReminder"]
                await channel.send(f"{message} ({game.next_clue})")

            # Wait out the rest of the interval
            await asyncio.sleep(
                (check_interval - gamedata.REMINDER_BUFFER) * 60 / game.game_speed
            )

        minutes_remaining -= check_interval

    # End of game, send debrief
    miscutils.send_image(
        LOCALIZATION_DATA["channels"]["clues"]["charlie"],
        gamedata.MASTER_PATHS["debrief"],
        game.guild,
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
    game = ctx.bot.d.games[ctx.guild_id]
    if game.automatic and not game.start_time:
        await ctx.respond(LOCALIZATION_DATA["errors"]["GameNotStarted"])
        return
    for character, role in game.char_roles().items():
        if role.id in ctx.member.role_ids:
            break
    else:
        await ctx.respond(LOCALIZATION_DATA["errors"]["NoCharacterRoles"])
        return

    char_channel = miscutils.get_text_channels(game.guild)[
        LOCALIZATION_DATA["channels"]["clues"][character.lower()]
    ]

    if game.search_cards:
        search = random.choice(game.search_cards)
        game.search_cards.remove(search)
        image = miscutils.get_image(dirs.SEARCHING_DIR, search)
        miscutils.send_image(char_channel, image, game.guild)

    else:
        # out of unique cards
        await char_channel.send(loc["search"]["NothingFound"])


@plugin.command()
@lightbulb.option("character_role", "the role of the character who gets the card", type=hikari.Role)
@lightbulb.command(
    loc["ten_min_card"]["name"],
    loc["ten_min_card"]["description"],
    aliases=loc["ten_min_card"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def ten_min_card(ctx: lightbulb.Context) -> None:
    """Assign the 10 minute card to another player"""
    game = ctx.bot.d.games[ctx.guild_id]
    character = ctx.options.character_role.name

    if character.title() not in game.char_roles():
        await ctx.respond(LOCALIZATION_DATA["errors"]["PlayerNotFound"])
        return

    game.ten_char = character.lower()

    await ctx.respond(loc["ten_min_card"]["Assigned"])


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
