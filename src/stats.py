import requests

API = ""
GAMES_PLAYED = "games-played"
PDF_EXPORT = "pdfs-created"
COMMANDS_RUN = "commands-run"
PLAYER_MESSAGES = "player-messages"

def increment(counter: str):
    # requests.get(API + counter)
    return

def increment_games_started(lang: str):
    increment(GAMES_PLAYED)
    if lang:
        increment(f"{GAMES_PLAYED}-{lang}")

def increment_pdfs():
    increment(PDF_EXPORT)

def increment_commands_run():
    increment(COMMANDS_RUN)

def increment_player_messages():
    increment(PLAYER_MESSAGES)
