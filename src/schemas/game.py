from typing import Any

from src.core.game import Game
from src.core.steps import step_mapping
from src.schemas.base import DynamoDBBaseModel


class GameModel(DynamoDBBaseModel):
    game_id: str
    game: Game
    game_step: str

    def __init__(self, **kwargs) -> None:
        game_step = kwargs["game"].current_step.__class__.__name__
        super().__init__(**kwargs, game_step=game_step)

    @classmethod
    def from_item(cls, item: dict[str, Any]) -> "GameModel":
        current_step_data = item["game"].pop("current_step")
        step_instance = step_mapping[item["game_step"]](**current_step_data)
        return cls(
            game_id=item["SK"].split("#")[-1],
            game=Game(**item["game"], current_step=step_instance),
        )

    def to_item(self) -> dict[str, Any]:
        return {"PK": self.pk, "SK": self.sk, **self.dict(exclude={"game_id"})}

    @property
    def pk(self) -> str:
        return f"game"

    @property
    def sk(self) -> str:
        return f"game#{self.game_id}"
