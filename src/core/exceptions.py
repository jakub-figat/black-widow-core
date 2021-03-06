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


class InvalidPayloadBody(GameError):
    pass


class StoreError(Exception):
    pass


class NoStoreSet(StoreError):
    pass
