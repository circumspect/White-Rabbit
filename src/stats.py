import requests

API = "https://api.countapi.xyz/hit/white-rabbit-bot/"
GAMES_PLAYED = "games-played"
PDF_EXPORT = "pdfs-created"
COMMANDS_RUN = "commands-run"
PLAYER_MESSAGES = "player-messages"

def increment(counter: str):
    requests.get(API + counter)

def increment_games_started(lang: str):
    increment(GAMES_PLAYED)
    if lang:
        increment(f"{GAMES_PLAYED}-{lang}")

def increment_pdfs():
    increment(PDF_EXPORT)

def increment_commands_run():
    increment(COMMANDS_RUN)

