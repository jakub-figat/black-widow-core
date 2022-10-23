from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


def to_camel_case(field_name: str) -> str:
    words = field_name.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        alias_generator = to_camel_case
        allow_population_by_field_name = True


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
