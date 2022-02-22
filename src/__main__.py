# Built-in
import asyncio
import sys
from os import environ

import lightbulb
import requests
import hikari

from utils import (
    constants,
    dirs,
    envvars,
    rabbit,
    miscutils,
    errors,
    gamedata,
)
from utils.localization import LOCALIZATION_DATA

# Minimum Python version check
if sys.version_info < (3, 6):
    sys.exit(
        "The White Rabbit does not support Python versions below 3.6."
        " Please install a newer version"
    )

# Clear .pkl files on startup to avoid export bug
miscutils.delete_files(dirs.FONT_DIR, "pkl")


# Localization
BOT_CHANNEL = LOCALIZATION_DATA["channels"]["bot-channel"]
SPECTATOR_ROLE = LOCALIZATION_DATA["spectator-role"]


# Import bot token
try:
    token = envvars.get_env_var("TOKEN")
except FileNotFoundError:
    r = requests.get(constants.BLANK_DOTENV_URL)
    with open(envvars.ENV_FILE, "x") as env:
        env.write(r.content)
    sys.exit(LOCALIZATION_DATA["errors"]["MissingDotEnv"])

bot = lightbulb.BotApp(
    token=token, prefix=constants.COMMAND_PREFIX, intents=hikari.Intents.ALL
)

bot.d.games = {}
bot.d.dev_ids = []

if dirs.DEV_ID_FILE.exists():
    with open(dirs.DEV_ID_FILE) as f:
        for line in f.readlines():
            line = line.strip()
            if line and line.isdigit():
                # Ignore any lines that can't be read as numbers
                # This is mostly helpful for commenting out ids
                # when testing so you don't need to delete lines
                bot.d.dev_ids.append(int(line))
else:
    # Create file if it doesn't exist
    print(f"No {dirs.DEV_ID_FILE.name} found, making empty file")
    with open(dirs.DEV_ID_FILE, "x") as f:
        pass
if environ.get("DEV_ID"):
    bot.d.dev_ids.append(int(environ.get("DEV_ID")))


@bot.listen()
async def on_ready(event: hikari.StartedEvent):
    await bot.update_presence(
        activity=hikari.Activity(
            name=LOCALIZATION_DATA["title"], type=hikari.ActivityType.PLAYING
        )
    )


@bot.check()
def is_bot_channel(ctx):
    """Only allow commands in #bot-channel"""
    if ctx.get_channel().name == BOT_CHANNEL:
        return True
    raise errors.NotBotChannel()


@bot.check()
def is_not_spectator(ctx):
    """Don't let spectators run commands"""
    if SPECTATOR_ROLE in [role.name for role in ctx.member.get_roles()]:
        raise errors.Spectator()
    return True


@bot.listen()
async def on_guild_message(event: hikari.GuildMessageCreateEvent):
    bot.d.games.setdefault(event.guild_id, gamedata.Data(event.get_guild()))


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    """Default error catcher for commands"""
    bot_channel = miscutils.get_text_channels(event.context.get_guild())[BOT_CHANNEL]
    # Failed a check
    if isinstance(event.exception, lightbulb.errors.CheckFailure):
        # Check if running debug command without being listed as developer
        if isinstance(event.exception.__cause__, errors.DevOnly):
            await event.context.respond(
                LOCALIZATION_DATA["errors"]["MissingDeveloperPermissions"]
            )

        # Check if user is spectator
        elif isinstance(event.exception.__cause__, errors.Spectator):
            await event.context.respond(
                LOCALIZATION_DATA["errors"]["SpectatorCommandAttempt"]
            )

        # Commands must be in bot-channel
        elif isinstance(event.exception.__cause__, errors.NotBotChannel):
            await bot_channel.send(
                f"{event.context.author.mention} "
                + LOCALIZATION_DATA["errors"]["CommandInWrongChannel"],
                user_mentions=[event.context.author.id],
            )
        # Automatic/manual check
        elif isinstance(event.exception.__cause__, errors.ManualCommandInAuto):
            await event.context.respond(
                LOCALIZATION_DATA["errors"]["ManualCommandInAuto"]
            )
        else:
            # Couldn't determine a specific error; tell user to check console
            await event.context.respond(
                LOCALIZATION_DATA["errors"]["GenericCheckFailure"]
            )
        return

    elif isinstance(event.exception, lightbulb.errors.CommandInvocationError):
        if isinstance(event.exception.original, errors.MotivesUnshuffled):
            await event.context.respond(
                LOCALIZATION_DATA["commands"]["manual"]["send_motives"]["NeedToShuffle"]
            )
            return
        elif isinstance(event.exception.original, errors.CluesNotShuffled):
            await event.context.respond(
                LOCALIZATION_DATA["commands"]["manual"]["clue"]["CluesNotShuffled"]
            )
            return
        elif isinstance(event.exception.original, errors.CluesNotAssigned):
            await event.context.respond(
                LOCALIZATION_DATA["commands"]["manual"]["clue"]["CluesNotAssigned"]
            )
            return
        elif isinstance(event.exception.original, errors.CluesNotAssigned):
            await event.context.respond(LOCALIZATION_DATA["errors"]["NotEnoughPlayers"])
            return
        elif isinstance(event.exception.original, errors.MissingCharlie):
            await event.context.respond(LOCALIZATION_DATA["errors"]["MissingCharlie"])
            return
        elif isinstance(event.exception.original, errors.BadInput):
            await event.context.respond(LOCALIZATION_DATA["errors"]["UserInputError"])
            return
        elif isinstance(event.exception.original, errors.GameAlreadyStarted):
            await event.context.respond(LOCALIZATION_DATA["errors"]["AlreadyStarted"])
            return
        elif isinstance(event.exception.original, errors.GameAlreadyInitialized):
            await event.context.respond(
                LOCALIZATION_DATA["errors"]["AlreadyInitialized"]
            )
            return

    # Bad input
    elif isinstance(event.exception, lightbulb.errors.ConverterFailure):
        await event.context.respond(LOCALIZATION_DATA["errors"]["UserInputError"])
        return

    # Can't find command
    elif isinstance(event.exception, lightbulb.errors.CommandNotFound):
        await event.context.respond(LOCALIZATION_DATA["errors"]["CommandNotFound"])
        return

    # Everything else
    await event.context.respond(LOCALIZATION_DATA["errors"]["UnknownError"])
    raise event.exception


for extension in (rabbit.WHITE_RABBIT_DIR / "src" / "extensions").iterdir():
    bot.load_extensions(f"extensions.{extension.stem}")

print("Logging in...")
bot.run()
