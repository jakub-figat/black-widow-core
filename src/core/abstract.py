from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel


if TYPE_CHECKING:
    from src.core.game import GameState


class GameStep(BaseModel, ABC):
    @classmethod
    @abstractmethod
    def run(cls, *args, **kwargs) -> Any:
        raise NotImplementedError


class GameStateStore(BaseModel, ABC):
    @abstractmethod
    def save_game_state(self, game_state: "GameState") -> Any:
        raise NotImplementedError

    @abstractmethod
    def load_game_state(self) -> "GameState":
        raise NotImplementedError
