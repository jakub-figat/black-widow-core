from typing import Any

from src.core.game import Game
from src.schemas.base import DynamoDBBaseModel


class GameModel(DynamoDBBaseModel):
    game_id: str
    game: Game

    @classmethod
    def from_item(cls, item: dict[str, Any]) -> "GameModel":
        return cls(game_id=item["PK"].split("#")[-1], game=Game(**item["game"]))

    def to_item(self) -> dict[str, Any]:
        return {"PK": self.pk, "SK": self.sk, "game": self.game.dict()}

    @property
    def pk(self) -> str:
        return f"games#{self.game_id}"

    @property
    def sk(self) -> str:
        return f"games#{self.game_id}"
