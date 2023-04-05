from typing import Dict, Optional

from discord.ext import commands
from discord import TextChannel

from data.gamedata import Data


class Context(commands.Context):
    game: Data
    character: Optional[str]
    text_channels: Dict[str, TextChannel]


class Bot(commands.Bot):
    games: Dict[int, Data]
