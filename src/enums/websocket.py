from enum import Enum


class Action(str, Enum):
    LIST_LOBBIES = "listLobbies"
    CREATE_LOBBY = "createLobby"
    JOIN_LOBBY = "joinLobby"
    LEAVE_LOBBY = "leaveLobby"
    LIST_GAMES = "listGames"


class RouteKey(str, Enum):
    CONNECT = "$connect"
    DISCONNECT = "$disconnect"


class PayloadType(str, Enum):
    INFO = "info"
    ERROR = "error"
    VALIDATION_ERROR = "validationError"
    INVALID_PAYLOAD = "invalidPayload"
    LOBBIES_LIST = "lobbiesList"
    LOBBY_UPDATED = "lobbyUpdated"
    LOBBY_DELETED = "lobbyDeleted"
    GAMES_LIST = "gamesList"
    GAME_UPDATED = "gameUpdated"
    GAME_DELETED = "gameDeleted"
    GAME_DETAIL = "gameDetail"
