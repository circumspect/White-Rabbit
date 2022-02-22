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