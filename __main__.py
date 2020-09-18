import AiMDB
from discord.ext import commands

bot = commands.Bot(command_prefix="!")
bot.add_cog(AiMDB.AliceIsMissing(bot))

with open("token.txt") as token_file:
    token = token_file.read()
bot.run(token)
