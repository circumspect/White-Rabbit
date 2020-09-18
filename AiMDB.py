import discord
import time
from discord.ext import commands

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f"Bot has logged in as {bot}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)


@bot.command()
async def start(ctx):
    await ctx.send('Starting the game!')


with open("token.txt") as token_file:
    token = token_file.read()

bot.run(token)
