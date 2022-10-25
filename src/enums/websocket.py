from enum import Enum


class Action(str, Enum):
    LIST_LOBBIES = "listLobbies"
    CREATE_LOBBY = "createLobby"
    LEAVE_LOBBY = "leaveLobby"


class RouteKey(str, Enum):
    CONNECT = "$connect"
    DISCONNECT = "$disconnect"


class PayloadType(str, Enum):
    INVALID_PAYLOAD = "invalidPayload"
    LOBBIES_LIST = "lobbiesList"
