# Built-in
import asyncio
import sys
# 3rd-party
import discord
from discord.ext import commands
from dotenv import dotenv_values
import requests
# Local
import gamedata
import utils

# Enable Server Members gateway intent to find all users
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.games = {}


@bot.event
async def on_ready():
    # Set custom status
    await bot.change_presence(activity=discord.Game("Alice is Missing"))


@bot.check
def check_channel(ctx):
    """Only allow commands in #bot-channel"""

    return ctx.channel.name == "bot-channel"


@bot.check
def not_spectator(ctx):
    """Don't let spectators run commands"""
    
    return "spectator" not in [role.name.lower() for role in ctx.author.roles]


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


@bot.event
async def on_command_error(ctx, error):
    """Default error catcher for commands"""

    bot_channel = utils.get_text_channels(ctx.guild)["bot-channel"]
    ctx.game = bot.games.setdefault(ctx.guild.id, gamedata.Data(ctx.guild))

    # Failed a check
    if isinstance(error, commands.errors.CheckFailure):
        # Commands must be in bot-channel
        if ctx.channel.name != "bot-channel" and utils.is_command(ctx.message.clean_content):
            asyncio.create_task(bot_channel.send(f"{ctx.author.mention} You can only use commands in {bot_channel.mention}!"))
            return
        
        # TODO: Check if running debug command without being in dev_ids.txt
        

        # Automatic/manual check
        if ctx.game.automatic:
            asyncio.create_task(ctx.send("Can't do that, are you running a manual command in automatic mode?"))
            return
        asyncio.create_task(ctx.send("You can't do that!"))

    # Bad input
    elif isinstance(error, commands.errors.UserInputError):
        asyncio.create_task(ctx.send("Can't understand input!"))

    # Can't find command
    elif isinstance(error, commands.errors.CommandNotFound):
        asyncio.create_task(ctx.send("Command not found!"))

    # Everything else
    else:
        asyncio.create_task(ctx.send("Unknown error: check console!"))
        raise error

# Load all extensions
PLUGINS = ["about", "admin", "debug", "export", "game", "manual", "players", "settings"]
for plugin in PLUGINS:
    bot.load_extension(plugin)

# Import bot token
try:
    bot.run(dotenv_values(utils.ENV_FILE)["TOKEN"])
except FileNotFoundError:
    r = requests.get(utils.BLANK_DOTENV_URL)
    with open(utils.ENV_FILE, 'x') as env:
        env.write(r.content)
    sys.exit("No dotenv file found! Downloading sample .env and shutting down")
except discord.errors.LoginFailure:
    sys.exit("Couldn't log in! Was the token incorrect?")
    