import requests

API = "https://api.countapi.xyz/hit/white-rabbit-bot/"
GAMES_PLAYED_COUNTER = API + "games-played"
PDF_EXPORT_COUNTER = API + "pdfs-created"
COMMANDS_RUN_COUNTER = API + "commands-run"

def increment(counter: str):
    requests.get(API + counter)

def increment_games_started(lang: str):
    increment(GAMES_PLAYED_COUNTER)
    if lang:
        increment(f"{GAMES_PLAYED_COUNTER}-{lang}")

def increment_pdfs():
    increment(PDF_EXPORT_COUNTER)

def increment_commands_run():
    increment(COMMANDS_RUN_COUNTER)
