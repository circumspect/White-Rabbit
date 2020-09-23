# Built-in
import asyncio
# 3rd-party
import discord
from discord.ext import commands
# Local
import utils
import gamedata

bot = commands.Bot(command_prefix="!")
bot.games = {}


@bot.event
async def on_ready():
    # Set custom status
    await bot.change_presence(activity=discord.Game("Alice is Missing"))


@bot.check
def check_channel(ctx):
    return ctx.channel.name == "bot-channel"


@bot.check
def not_spectator(ctx):
    return "spectator" not in [role.name.lower() for role in ctx.author.roles]


@bot.before_invoke
async def before_invoke(ctx):
    ctx.game = bot.games.setdefault(ctx.guild.id, gamedata.Data(ctx.guild))
    ctx.text_channels = {
        channel.name: channel
        for channel in ctx.guild.text_channels
    }
    ctx.character = None
    for role in ctx.author.roles:
        if role.name.lower() in gamedata.CHARACTERS:
            ctx.character = role.name.lower()


@bot.event
async def on_command_error(ctx, error):
    ctx.text_channels = {
        channel.name: channel
        for channel in ctx.guild.text_channels
    }
    bot_channel = ctx.text_channels["bot-channel"]
    if isinstance(error, discord.ext.commands.errors.UserInputError):
        asyncio.create_task(ctx.send("Can't understand input!"))
    elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
        asyncio.create_task(ctx.send("Command not found!"))
    elif isinstance(error, discord.ext.commands.errors.CheckFailure):
        if ctx.channel.name != "bot-channel":
            asyncio.create_task(ctx.send(f"You can only use commands in {bot_channel.mention}"))
            return
        asyncio.create_task(ctx.send("You can't do that"))
    else:
        asyncio.create_task(ctx.send("Unknown error: check console!"))
        raise error


# Load all extensions
PLUGINS = ["admin", "debug", "game", "manual", "players", "settings"]
for plugin in PLUGINS:
    bot.load_extension(plugin)

print(f"Cogs loaded: {', '.join(bot.cogs.keys())}")

# Import bot token
with open(utils.WHITE_RABBIT_DIR / "token.txt") as token_file:
    token = token_file.read()
bot.run(token)
