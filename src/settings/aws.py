from pydantic import BaseSettings, Field


class AWSSettings(BaseSettings):
    dynamodb_games_table_name: str = Field(..., env="DYNAMODB_GAMES_TABLE_NAME")
