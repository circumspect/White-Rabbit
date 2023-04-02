from typing import Dict, List, Optional

from discord.ext import commands
from discord import TextChannel

from data.gamedata import Data


class Context(commands.Context):
    game: Data
    character: Optional[str]
    text_channels: Dict[str, TextChannel]


class Bot(commands.Bot):
    dev_ids: List[int]
    games: Dict[int, Data]
