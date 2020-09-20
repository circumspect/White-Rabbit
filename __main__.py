import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("Alice is Missing"))


for extension in ["admin", "game", "players"]:
    bot.load_extension(extension)

with open("token.txt") as token_file:
    token = token_file.read()
bot.run(token)
