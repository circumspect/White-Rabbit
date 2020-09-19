from discord.ext import commands

bot = commands.Bot(command_prefix="!")

for extension in ["AiMDB", "dev"]:
    bot.load_extension(extension)

with open("token.txt") as token_file:
    token = token_file.read()
bot.run(token)
