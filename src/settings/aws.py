from pydantic import BaseSettings, Field


class AWSSettings(BaseSettings):
    aws_access_key: str = Field(..., env="AWS_ACCESS_KEY")
    aws_secret_key: str = Field(..., env="AWS_SECRET_KEY")
    region: str = Field("eu-central-1", env="REGION")
    dynamodb_games_table_name: str = Field(..., env="DYNAMODB_GAMES_TABLE_NAME")
