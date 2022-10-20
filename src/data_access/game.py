from src.data_access.dynamodb import DynamoDBDataAccess
from src.schemas.game import GameModel


class GameDataAccess(DynamoDBDataAccess[str, str, GameModel]):
    _model = GameModel
