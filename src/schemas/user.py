from typing import Any

from src.schemas.base import DynamoDBBaseModel


class UserModel(DynamoDBBaseModel):
    email: str
    games_ids: list[str] = []
    lobbies_ids: list[str] = []
    connection_ids: list[str] = []

    @classmethod
    def from_item(cls, item: dict[str, Any]) -> "DynamoDBBaseModel":
        email = item.pop("SK").split("#")[-1]
        item.pop("PK")
        return cls(email=email, **item)

    def to_item(self) -> dict[str, Any]:
        return {"PK": self.pk, "SK": self.sk, **self.dict(exclude={"email"})}

    @property
    def pk(self) -> str:
        return f"user"

    @property
    def sk(self) -> str:
        return f"user#{self.email}"
