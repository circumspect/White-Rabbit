CHARACTERS = {
    "charlie": "Charlie Barnes",
    "dakota": "Dakota Travis",
    "evan": "Evan Holwell",
    "jack": "Jack Briarwood",
    "julia": "Julia North",
}

class Game:
    def __init__(self, guild):
        self.guild = guild
        self.setup = False
        self.started = False
        self.show_timer = False
