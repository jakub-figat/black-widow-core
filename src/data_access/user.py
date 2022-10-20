from src.data_access.dynamodb import DynamoDBDataAccess
from src.schemas.user import UserModel


class UserDataAccess(DynamoDBDataAccess[str, str, UserModel]):
    _model = UserModel
