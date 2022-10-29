from abc import ABC, abstractmethod
from typing import Any

from src.core.schemas import BaseSchema


class DynamoDBBaseModel(BaseSchema, ABC):
    @classmethod
    @abstractmethod
    def from_item(cls, item: dict[str, Any]) -> "DynamoDBBaseModel":
        pass

    @abstractmethod
    def to_item(self) -> dict[str, Any]:
        pass

    @property
    @abstractmethod
    def pk(self) -> str:
        pass

    @property
    @abstractmethod
    def sk(self) -> str:
        pass

    @property
    def key(self) -> dict[str, Any]:
        return {"pk": self.pk, "sk": self.sk}
