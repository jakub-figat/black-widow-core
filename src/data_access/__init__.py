from src.data_access.user import UserDataAccess
from src.settings import settings


user_data_access = UserDataAccess(table_name=settings.dynamodb_games_table_name)
