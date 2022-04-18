from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel


if TYPE_CHECKING:
    from src.core.game import GameState


class GameStateStore(BaseModel, ABC):
    @abstractmethod
    def save_game_state(self, game_state: "GameState") -> Any:
        raise NotImplementedError

    @abstractmethod
    def load_game_state(self) -> "GameState":
        raise NotImplementedError


class GameStateAsyncStore(BaseModel, ABC):
    @abstractmethod
    async def save_game_state_async(self, game_state: "GameState") -> Any:
        raise NotImplementedError

    @abstractmethod
    async def load_game_state_async(self) -> "GameState":
        raise NotImplementedError
