# Built-in
import asyncio
import sys
from os import environ
# 3rd-party
import discord
from discord.ext import commands
from dotenv import dotenv_values
import requests
# Local
import constants
import gamedata
import utils
from localization import LOCALIZATION_DATA

# Enable Server Members gateway intent to find all users
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
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
def check_channel(ctx):
    """Only allow commands in #bot-channel"""

    return ctx.channel.name == BOT_CHANNEL


@bot.check
def not_spectator(ctx):
    """Don't let spectators run commands"""

    return SPECTATOR_ROLE not in [role.name for role in ctx.author.roles]


@bot.before_invoke
async def before_invoke(ctx):
    """Attaches stuff to ctx for convenience"""

    # that guild's game
    ctx.game = bot.games.setdefault(ctx.guild.id, gamedata.Data(ctx.guild))

    # access text channels by name
    ctx.text_channels = {
        channel.name: channel
        for channel in ctx.guild.text_channels
    }

    # Character that the author is
    ctx.character = None
    for role in ctx.author.roles:
        if role.name.lower() in gamedata.CHARACTERS:
            ctx.character = role.name.lower()
            break


@bot.event
async def on_command_error(ctx, error):
    """Default error catcher for commands"""

    bot_channel = utils.get_text_channels(ctx.guild)[BOT_CHANNEL]
    ctx.game = bot.games.setdefault(ctx.guild.id, gamedata.Data(ctx.guild))

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

        # Commands must be in bot-channel
        if ctx.channel.name != BOT_CHANNEL and utils.is_command(ctx.message.clean_content):
            asyncio.create_task(bot_channel.send(f"{ctx.author.mention} " + LOCALIZATION_DATA["errors"]["CommandInWrongChannel"]))
            return

        # TODO: Check if running debug command without being in dev_ids.txt


        # Automatic/manual check
        if ctx.game.automatic:
            asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["ManualCommandInAuto"]))
            return

        asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["GenericCheckFailure"]))

    # Bad input
    elif isinstance(error, commands.errors.UserInputError):
        asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["UserInputError"]))

    # Can't find command
    elif isinstance(error, commands.errors.CommandNotFound):
        asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["CommandNotFound"]))

    # Everything else
    else:
        asyncio.create_task(ctx.send(LOCALIZATION_DATA["errors"]["UnknownError"]))
        raise error

# Load all extensions
PLUGINS = ["about", "admin", "debug", "export", "game", "manual", "players", "settings"]
for plugin in PLUGINS:
    bot.load_extension(plugin)

# Import bot token
try:
    token = environ.get('TOKEN') or dotenv_values(constants.ENV_FILE)["TOKEN"]
    print("Logging in...")
    bot.run(token)
except FileNotFoundError:
    r = requests.get(constants.BLANK_DOTENV_URL)
    with open(constants.ENV_FILE, 'x') as env:
        env.write(r.content)
    sys.exit(LOCALIZATION_DATA["errors"]["MissingDotEnv"])
except discord.errors.LoginFailure:
    sys.exit(LOCALIZATION_DATA["errors"]["LoginFailure"])
