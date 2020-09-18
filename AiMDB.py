import discord
import time

client = discord.Client()

@client.event
async def on_ready():
    print('Bot has logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    
    #
    if message.content.startswith('!start'):
        await message.channel.send('Starting the game!')

with open("token.txt") as token_file:
    token = token_file.read()

client.run(token)