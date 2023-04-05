# pyright: reportShadowedImports=false

# Built-in
import asyncio
import logging
import sys
from typing import Union
# 3rd-party
import discord
from discord.ext import commands
import logging_tree
import requests
# Local
from bot import WhiteRabbit
from cogs.debug import DEBUG_COMMAND_LIST
from data import cards, constants, dirs
from data.wrappers import Context, Data
from data.localization import LOCALIZATION_DATA
import envvars
import utils

VERSION_CHECK_ERROR = """
The White Rabbit does not support Python versions below 3.10.
Please install a newer version.
"""

logging.getLogger().handlers.clear()
discord.utils.setup_logging()

if envvars.DEBUG:
    print(logging_tree.format.build_description())

# Minimum Python version check
if sys.version_info < (3, 10):
    sys.exit(VERSION_CHECK_ERROR)

# Clear .pkl files on startup to avoid export bug
utils.delete_files(dirs.FONT_DIR, "pkl")

# Enable Server Members gateway intent to find all users
intents = discord.Intents.all()

bot = WhiteRabbit(
    command_prefix=commands.when_mentioned_or(constants.COMMAND_PREFIX),
    intents=intents
)
bot.games = {}

# Localization
BOT_CHANNEL = LOCALIZATION_DATA["channels"]["bot-channel"]
SPECTATOR_ROLE = LOCALIZATION_DATA["spectator-role"]


@bot.event
async def on_ready():
    # Set custom status
    await bot.change_presence(
        activity=discord.Game(LOCALIZATION_DATA["title"])
    )


@bot.check
def check_channel(ctx: Context) -> bool:
    """Only allow commands in #bot-channel"""

    assert ctx.command
    assert isinstance(ctx.channel, Union[discord.TextChannel, discord.Thread])

    if ctx.channel.name == BOT_CHANNEL:
        return True

    return ctx.command.name in (
        "server_setup",
        LOCALIZATION_DATA["commands"]["admin"]["server_setup"]
    )


@bot.check
def not_spectator(ctx: Context):
    """Don't let spectators run commands"""

    assert isinstance(ctx.author, discord.Member)

    return SPECTATOR_ROLE not in [role.name for role in ctx.author.roles]


@bot.before_invoke
async def before_invoke(ctx: Context):
    """Attaches stuff to ctx for convenience"""

    assert ctx.guild
    assert isinstance(ctx.author, discord.Member)

    # that guild's game
    ctx.game = bot.games.setdefault(ctx.guild.id, Data(ctx.guild))

    # access text channels by name
    ctx.text_channels = {
        channel.name: channel
        for channel in ctx.guild.text_channels
    }

    # Character that the author is
    ctx.character = None
    for role in ctx.author.roles:
        if role.name in cards.ROLES_TO_NAMES:
            ctx.character = cards.ROLES_TO_NAMES[role.name]
            break


@bot.event
async def on_command_error(ctx: Context, error):
    """Default error catcher for commands"""

    assert ctx.guild
    assert isinstance(ctx.author, discord.Member)

    bot_channel = utils.get_text_channels(ctx.guild)[BOT_CHANNEL]
    ctx.game = bot.games.setdefault(ctx.guild.id, Data(ctx.guild))

    # Failed a check
    if isinstance(error, commands.errors.CheckFailure):
        # Check if user is spectator
        if SPECTATOR_ROLE in [role.name for role in ctx.author.roles]:
            asyncio.create_task(
                ctx.send(
                    LOCALIZATION_DATA["errors"]["SpectatorCommandAttempt"]
                )
            )

            return

        assert isinstance(
            ctx.channel,
            Union[discord.TextChannel, discord.Thread]
        )

        # Commands must be in bot-channel
        if ctx.channel.name != BOT_CHANNEL and utils.is_command(ctx.message.clean_content):
            asyncio.create_task(bot_channel.send(
                f"{ctx.author.mention} "
                + LOCALIZATION_DATA["errors"]["CommandInWrongChannel"]
            ))
            return

        # Check if running debug command without being listed as developer
        # TODO: is there a better way to check this than testing against
        # every command/alias?
        if envvars.DEBUG:
            message = ctx.message.clean_content
            for command in DEBUG_COMMAND_LIST:
                command_loc = LOCALIZATION_DATA["commands"]["debug"][command]
                aliases: list = command_loc["aliases"]
                aliases.append(command_loc["name"])
                for alias in aliases:
                    if message.startswith(constants.COMMAND_PREFIX + alias):
                        asyncio.create_task(
                            ctx.send(LOCALIZATION_DATA["errors"]["MissingDeveloperPermissions"])
                        )
                        return

        # Automatic/manual check
        if ctx.game.automatic:
            asyncio.create_task(
                ctx.send(LOCALIZATION_DATA["errors"]["ManualCommandInAuto"])
            )
            return

        # Couldn't determine a specific error; tell user to check console
        asyncio.create_task(
            ctx.send(LOCALIZATION_DATA["errors"]["GenericCheckFailure"])
        )

    # Bad input
    elif isinstance(error, commands.errors.UserInputError):
        asyncio.create_task(
            ctx.send(LOCALIZATION_DATA["errors"]["UserInputError"])
        )

    # Can't find command
    elif isinstance(error, commands.errors.CommandNotFound):
        asyncio.create_task(
            ctx.send(LOCALIZATION_DATA["errors"]["CommandNotFound"])
        )

    # Everything else
    else:
        asyncio.create_task(
            ctx.send(LOCALIZATION_DATA["errors"]["UnknownError"])
        )
        raise error


# Import bot token
try:
    token = envvars.TOKEN
    assert isinstance(token, str)
    logging.info("Logging in...")
    bot.run(token, log_handler=None)
except FileNotFoundError:
    r = requests.get(constants.BLANK_DOTENV_URL)
    with open(envvars.ENV_FILE, 'xb') as env:
        env.write(r.content)
    sys.exit(LOCALIZATION_DATA["errors"]["MissingDotEnv"])
except discord.errors.LoginFailure:
    sys.exit(LOCALIZATION_DATA["errors"]["LoginFailure"])
