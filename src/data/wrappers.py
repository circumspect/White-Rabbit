from typing import List

from discord.ext import commands
from discord import TextChannel

from data.gamedata import Data


class Context(commands.Context):
    game: Data
    text_channels: List[TextChannel]

class Bot(commands.Bot):
    dev_ids: List[str]
