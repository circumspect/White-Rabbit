import sys

import lightbulb
import requests

import constants
import envvars
from localization import LOCALIZATION_DATA

# Import bot token
try:
    token = envvars.get_env_var("TOKEN")
except FileNotFoundError:
    r = requests.get(constants.BLANK_DOTENV_URL)
    with open(envvars.ENV_FILE, 'x') as env:
        env.write(r.content)
    sys.exit(LOCALIZATION_DATA["errors"]["MissingDotEnv"])

bot = lightbulb.BotApp(token=token, prefix="?")

for extension in ["about", "debug"]:
    bot.load_extensions(f"extensions.{extension}")

print("Logging in...")
bot.run()