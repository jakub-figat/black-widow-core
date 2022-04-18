class GameError(Exception):
    pass


class InvalidCardComparison(GameError):
    pass


class InvalidNumberOfUsers(GameError):
    pass


class FirstUserNotFound(GameError):
    pass


class InvalidUser(GameError):
    pass


class InvalidPayloadType(GameError):
    pass
