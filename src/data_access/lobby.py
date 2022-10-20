from src.data_access.dynamodb import DynamoDBDataAccess
from src.schemas.lobby import LobbyModel


class LobbyDataAccess(DynamoDBDataAccess[str, str, LobbyModel]):
    _model = LobbyModel
