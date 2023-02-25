# Built-in

# 3rd-party
from discord.ext import commands

# Local
from localization import LOCALIZATION_DATA

# Localization
BOT_CHANNEL = LOCALIZATION_DATA["channels"]["bot-channel"]
SPECTATOR_ROLE = LOCALIZATION_DATA["spectator-role"]

class WhiteRabbit(commands.Bot):
    async def setup_hook(self) -> None:
        # here, we are loading extensions prior to sync to ensure we are syncing interactions defined in those extensions.

        # Load all extensions
        PLUGINS = ["about", "admin", "debug", "export", "game", "manual", "players", "settings"]
        for plugin in PLUGINS:
            await self.load_extension(f"cogs.{plugin}")

