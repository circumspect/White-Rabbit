import lightbulb
from lightbulb import commands

from utils import constants, miscutils
from utils.localization import LOCALIZATION_DATA

loc = LOCALIZATION_DATA["commands"]["about"]

plugin = lightbulb.Plugin("About")

@plugin.command()
@lightbulb.command(loc["credits"]["name"], loc["credits"]["description"], aliases=loc["credits"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def credits(ctx: lightbulb.Context) -> None:
    message = "\n".join([
        loc["credits"]["creators"],
        loc["credits"]["source"],
        constants.SOURCE_URL,
    ])
    message = miscutils.codeblock(message)
    await ctx.respond(message)


@plugin.command()
@lightbulb.command(loc["docs"]["name"], loc["docs"]["description"], aliases=loc["docs"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def credits(ctx: lightbulb.Context) -> None:
    message = "\n".join([
        loc["docs"]["documentation"],
        constants.DOCS_SHORT_URL,
    ])
    message = miscutils.codeblock(message)
    await ctx.respond(message)


def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
