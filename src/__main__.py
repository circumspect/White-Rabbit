# Built-in
import asyncio
import sys
from os import environ

import lightbulb
import requests
import hikari

from utils import constants, dirs, envvars, filepaths, rabbit, miscutils
from utils.localization import LOCALIZATION_DATA

# Minimum Python version check
if sys.version_info < (3, 6):
    sys.exit("The White Rabbit does not support Python versions below 3.6. Please install a newer version")

# Clear .pkl files on startup to avoid export bug
miscutils.delete_files(dirs.FONT_DIR, "pkl")


# Localization
BOT_CHANNEL = LOCALIZATION_DATA["channels"]["bot-channel"]
SPECTATOR_ROLE = LOCALIZATION_DATA["spectator-role"]

# Import bot token
try:
    token = envvars.get_env_var("TOKEN")
except FileNotFoundError:
    r = requests.get(constants.BLANK_DOTENV_URL)
    with open(envvars.ENV_FILE, 'x') as env:
        env.write(r.content)
    sys.exit(LOCALIZATION_DATA["errors"]["MissingDotEnv"])

bot = lightbulb.BotApp(token=token, prefix=constants.COMMAND_PREFIX)

bot.d.games = {}
bot.d.dev_ids = []

try:
    with open(filepaths.DEV_ID_FILE) as f:
        for line in f.readlines():
            line = line.strip()
            if line:
                try:
                    # Ignore any lines that can't be read as numbers
                    # This is mostly helpful for commenting out ids
                    # when testing so you don't need to delete lines
                    bot.d.dev_ids.append(int(line))
                except ValueError:
                    pass
except FileNotFoundError:
    # Create file if it doesn't exist
    print("No " + filepaths.DEV_ID_FILE.name + " found, making empty file")
    with open(filepaths.DEV_ID_FILE, 'x') as f:
        pass

if environ.get("DEV_ID"):
    bot.d.dev_ids.append(int(environ.get("DEV_ID")))


for extension in (rabbit.WHITE_RABBIT_DIR / "src" / "extensions").iterdir():
    bot.load_extensions(f"extensions.{extension.stem}")

print("Logging in...")
bot.run()
