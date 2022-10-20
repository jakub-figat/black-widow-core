from typing import Any

from src.schemas.base import DynamoDBBaseModel


class UserModel(DynamoDBBaseModel):
    email: str
    games_ids: list[str] = []
    lobbies_ids: list[str] = []

    @classmethod
    def from_item(cls, item: dict[str, Any]) -> "DynamoDBBaseModel":
        email = item["PK"].split("#")[-1]
        return cls(email=email, games_ids=item["games_ids"], lobbies_ids=item["lobbies_ids"])

    def to_item(self) -> dict[str, Any]:
        return {"PK": self.pk, "SK": self.sk, **self.dict(exclude={"email"})}

    @property
    def pk(self) -> str:
        return f"games#user#{self.email}"

    @property
    def sk(self) -> str:
        return f"games#user#{self.email}"
