import datetime as dt
from functools import partial
from typing import Any

from pydantic import Field

from src.schemas.base import DynamoDBBaseModel


class LobbyModel(DynamoDBBaseModel):
    lobby_id: str
    users: list[str] = Field(default_factory=list, max_items=4)
    max_players: int = Field(default=3, le=4, ge=3)
    created_at: dt.datetime = Field(default_factory=partial(dt.datetime.now, tz=dt.timezone.utc))

    @classmethod
    def from_item(cls, item: dict[str, Any]) -> "LobbyModel":
        lobby_id = item["SK"].split("#")[-1]
        return cls(
            lobby_id=lobby_id,
            users=item["users"],
            max_players=item["max_players"],
            created_at=dt.datetime.fromisoformat(item["created_at"]),
        )

    def to_item(self) -> dict[str, Any]:
        lobby_dict = self.dict(exclude={"lobby_id"})
        lobby_dict["created_at"] = lobby_dict["created_at"].isoformat()
        return {"PK": self.pk, "SK": self.sk, **lobby_dict}

    @property
    def pk(self) -> str:
        return "lobby"

    @property
    def sk(self) -> str:
        return f"lobby#{self.lobby_id}"
