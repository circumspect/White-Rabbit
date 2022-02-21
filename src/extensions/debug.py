import lightbulb
from lightbulb import commands

import constants
from localization import LOCALIZATION_DATA
import utils

plugin = lightbulb.Plugin("Debug")
loc = LOCALIZATION_DATA["commands"]["debug"]


@plugin.command()
@lightbulb.command(loc["load"]["name"], loc["load"]["description"], aliases=loc["load"]["aliases"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def load(ctx: lightbulb.Context) -> None:
    ctx.app.reload_extensions(*ctx.app.extensions)
    await ctx.respond("Reloaded")


def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)