class GameError(Exception):
    pass


class InvalidUser(GameError):
    pass


class InvalidPayloadType(GameError):
    pass
