# Built-in
import asyncio
# 3rd-party
from discord.ext import commands
# Local
import utils
from localization import LOCALIZATION_DATA

loc = LOCALIZATION_DATA["commands"]["about"]

class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name=loc["credits"]["name"],
        aliases=loc["credits"]["aliases"],
        description=loc["credits"]["description"]
    )
    async def credits(self, ctx):
        """Prints information about the bot"""

        message = "\n".join([
            loc["credits"]["creators"],
            loc["credits"]["source"],
            utils.SOURCE_URL,
        ])
        message = utils.codeblock(message)
        asyncio.create_task(ctx.send(message))

    @commands.command(
        name=loc["docs"]["name"],
        aliases=loc["docs"]["aliases"],
        description=loc["docs"]["description"]
    )
    async def docs(self, ctx):
        """Link to the documentation"""

        message = "\n".join([
            loc["docs"]["documentation"],
            utils.DOCS_SHORT_URL,
        ])
        message = utils.codeblock(message)
        asyncio.create_task(ctx.send(message))


def setup(bot):
    bot.add_cog(About(bot))
