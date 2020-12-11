# Built-in
import asyncio
import sys
# 3rd-party
import discord
from discord.ext import commands
# Local
import gamedata
import utils

# See https://stackoverflow.com/questions/64524256/guild-members-not-working-correctly-discord-py
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
        if ctx.channel.name != "bot-channel" and utils.is_command(ctx.message.clean_content):
            asyncio.create_task(bot_channel.send(f"{ctx.author.mention} You can only use commands in {bot_channel.mention}!"))
            return

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
    with open(utils.WHITE_RABBIT_DIR / "token.txt") as token_file:
        token = token_file.read()
    bot.run(token)
except FileNotFoundError:
    sys.exit("Couldn't find token for the bot, shutting down!")
else:
    sys.exit("Something went wrong")

