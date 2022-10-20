from typing import Any

from pydantic import Field

from src.schemas.base import DynamoDBBaseModel


class LobbyModel(DynamoDBBaseModel):
    lobby_id: str
    users: list[str] = Field(default_factory=list, max_length=4)
    max_players: int = Field(default=3, le=4, ge=3)

    @classmethod
    def from_item(cls, item: dict[str, Any]) -> "LobbyModel":
        lobby_id = item["PK"].split("#")[-1]
        return cls(
            lobby_id=lobby_id, user_ids=item["users"], max_players=item["max_players"], max_score=item["max_score"]
        )

    def to_item(self) -> dict[str, Any]:
        return {"PK": self.pk, "SK": self.sk, **self.dict(exclude={"lobby_id"})}

    @property
    def pk(self) -> str:
        return f"games#lobby#{self.lobby_id}"

    @property
    def sk(self) -> str:
        return f"games#lobby#{self.lobby_id}"
