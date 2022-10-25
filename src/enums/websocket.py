from enum import Enum


class Action(str, Enum):
    LIST_LOBBIES = "listLobbies"
    CREATE_LOBBY = "createLobby"
    JOIN_LOBBY = "joinLobby"
    LEAVE_LOBBY = "leaveLobby"


class RouteKey(str, Enum):
    CONNECT = "$connect"
    DISCONNECT = "$disconnect"


class PayloadType(str, Enum):
    INFO = "info"
    ERROR = "error"
    VALIDATION_ERROR = "validationError"
    INVALID_PAYLOAD = "invalidPayload"
    LOBBIES_LIST = "lobbiesList"
