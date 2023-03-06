# Built-in
import asyncio
# 3rd-party
from discord.ext import commands
# Local
from data import constants
from data.gamedata import Context
from data.localization import LOCALIZATION_DATA
import utils

loc = LOCALIZATION_DATA["commands"]["about"]


class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name=loc["credits"]["name"],
        aliases=loc["credits"]["aliases"],
        description=loc["credits"]["description"]
    )
    async def credits(self, ctx: Context):
        """Prints information about the bot"""

        message = "\n".join([
            loc["credits"]["creators"],
            loc["credits"]["source"],
            constants.SOURCE_URL,
        ])
        message = utils.codeblock(message)
        asyncio.create_task(ctx.send(message))

    @commands.command(
        name=loc["docs"]["name"],
        aliases=loc["docs"]["aliases"],
        description=loc["docs"]["description"]
    )
    async def docs(self, ctx: Context):
        """Link to the documentation"""

        message = "\n".join([
            loc["docs"]["documentation"],
            constants.DOCS_SHORT_URL,
        ])
        message = utils.codeblock(message)
        asyncio.create_task(ctx.send(message))


async def setup(bot: commands.Bot):
    await bot.add_cog(About(bot))
