from typing import Any, Optional

from src.core.game import Game
from src.core.steps import STEP_MAPPING
from src.schemas.base import DynamoDBBaseModel


class GameModel(DynamoDBBaseModel):
    game_id: str
    game: Game
    game_step: str
    finished_at: Optional[int] = None  # datetime converted to seconds from epoch

    def __init__(self, **kwargs) -> None:
        game_step = kwargs["game"].current_step.__class__.__name__
        super().__init__(**kwargs, game_step=game_step)

    @classmethod
    def from_item(cls, item: dict[str, Any]) -> "GameModel":
        current_step_data = item["game"].pop("current_step")
        step_instance = STEP_MAPPING[item["game_step"]](**current_step_data)
        return cls(
            game_id=item["SK"].split("#")[-1],
            game=Game(**item["game"], current_step=step_instance),
            finished_at=item["finished_at"],
        )

    def to_item(self) -> dict[str, Any]:
        return {"PK": self.pk, "SK": self.sk, **self.dict(exclude={"game_id"})}

    @property
    def pk(self) -> str:
        return f"game"

    @property
    def sk(self) -> str:
        return f"game#{self.game_id}"
