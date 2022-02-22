import asyncio
import random
import lightbulb

from utils.localization import LOCALIZATION_DATA
from utils import constants, gamedata, errors

loc = LOCALIZATION_DATA["commands"]["manual"]

plugin = lightbulb.Plugin("Manual")


@lightbulb.Check
def is_manual(ctx: lightbulb.Context):
    """Only people with access to the code"""
    game = ctx.bot.d.games[ctx.guild_id]
    if game.automatic:
        raise errors.ManualCommandInAuto()
    return True


plugin.add_checks(is_manual)


@plugin.command()
@lightbulb.option("choice", "which poster of alice to use", type=int, default=0)
@lightbulb.command(
    loc["alice"]["name"], loc["alice"]["description"], aliases=loc["alice"]["aliases"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def alice(ctx: lightbulb.Context) -> None:
    """
    Sends a specified Alice poster, or a random one if no argument is
    passed

    This will also update the Alice value in the game data.
    """

    if ctx.options.choice < 0 or ctx.options.choice > 10:
        raise errors.BadInput()

    choice = ctx.options.choice if ctx.options.choice else random.randint(1, 10)
    game = ctx.bot.d.games[ctx.guild_id]
    game.alice = choice

    await game.send_alice()


@plugin.command()
@lightbulb.command(
    loc["shuffle_motives"]["name"],
    loc["shuffle_motives"]["description"],
    aliases=loc["shuffle_motives"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def shuffle_motives(ctx: lightbulb.Context) -> None:
    """Shuffle and assign motive cards"""
    game = ctx.bot.d.games[ctx.guild_id]
    await ctx.respond(loc["shuffle_motives"]["Shuffling"])

    game.shuffle_motives()

    # Console logging
    print(f"{constants.INFO_PREFIX}Shuffled motives!")
    print(game.motives)


@plugin.command()
@lightbulb.command(
    loc["send_motives"]["name"],
    loc["send_motives"]["description"],
    aliases=loc["send_motives"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def send_motives(ctx: lightbulb.Context) -> None:
    """Distributes motive cards"""
    game = ctx.bot.d.games[ctx.guild_id]
    await game.send_motives()


@plugin.command()
@lightbulb.option("time", "time to pull a card for", type=int)
@lightbulb.command(
    loc["clue"]["name"], loc["clue"]["description"], aliases=loc["clue"]["aliases"]
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def clue(ctx: lightbulb.Context) -> None:
    """
    Draws a clue card given a time

    Ex: !clue 40
    """
    # Check that clue exists at specified time
    if ctx.options.time not in gamedata.CLUE_TIMES:
        await ctx.respond(loc["clue"]["ClueNotFound"])
        return

    game = ctx.bot.d.games[ctx.guild_id]
    # This check is disabled to allow more flexibility when running in
    # manual mode if players want to decide who gets what clue. If you
    # wish ensure that players cannot draw each other's clues, uncomment
    # out the lines below
    #
    # Check that the person calling the command has the clue
    # Ignores this check for the 10 minute clue because that one
    # is assigned manually anyway
    # for role_id, role in game.char_roles().items():
    #     if role_id in ctx.member.role_ids:
    #         character = role.name
    #         break
    # else:
    #     await ctx.respond(LOCALIZATION_DATA["errors"]["NoCharacterRoles"])
    # if ctx.options.time != 10 and ctx.options.time not in game.clue_assignments[character]:
    #     await ctx.respond(loc["clue"]["NotYourClue"])
    #     return

    # Send the clue
    await game.send_clue(ctx.options.time)


@plugin.command()
@lightbulb.command(
    loc["shuffle_clues"]["name"],
    loc["shuffle_clues"]["description"],
    aliases=loc["shuffle_clues"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def shuffle_clues(ctx: lightbulb.Context) -> None:
    """(Re)shuffles the clue card piles"""
    game = ctx.bot.d.games[ctx.guild_id]
    await ctx.respond(loc["shuffle_clues"]["ShufflingClues"])
    game.shuffle_clues()
    # Console logging
    print(f"{constants.INFO_PREFIX}Shuffled clue piles!")
    print(game.picked_clues)


@plugin.command()
@lightbulb.command(
    loc["assign_times"]["name"],
    loc["assign_times"]["description"],
    aliases=loc["assign_times"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def assign_times(ctx: lightbulb.Context) -> None:
    """Randomizes and assigns clue times"""
    game = ctx.bot.d.games[ctx.guild_id]
    await ctx.respond(loc["assign_clues"]["AssigningClues"])

    game.assign_clues()
    # Console logging
    print(f"{constants.INFO_PREFIX}Assigned clue cards!")
    print(game.clue_assignments)


@plugin.command()
@lightbulb.command(
    loc["print_times"]["name"],
    loc["print_times"]["description"],
    aliases=loc["print_times"]["aliases"],
)
@lightbulb.implements(lightbulb.PrefixCommand)
async def print_times(ctx: lightbulb.Context) -> None:
    """
    Print out clue assignments in a code block
    """
    game = ctx.bot.d.games[ctx.guild_id]
    await game.send_times()


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
