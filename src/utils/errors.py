class WhiteRabbitError(Exception):
    pass


class DevOnly(WhiteRabbitError):
    pass


class Spectator(WhiteRabbitError):
    pass


class NotBotChannel(WhiteRabbitError):
    pass


class ManualCommandInAuto(WhiteRabbitError):
    pass


class MotivesUnshuffled(WhiteRabbitError):
    pass


class CluesNotShuffled(WhiteRabbitError):
    pass


class CluesNotAssigned(WhiteRabbitError):
    pass


class NotEnoughPlayers(WhiteRabbitError):
    pass


class MissingCharlie(WhiteRabbitError):
    pass


class BadInput(WhiteRabbitError):
    pass


class GameAlreadyStarted(WhiteRabbitError):
    pass


class GameAlreadyInitialized(WhiteRabbitError):
    pass
