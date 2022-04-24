from abc import ABC, abstractmethod
from typing import Any, Type

from pydantic import BaseModel

from src.core.exceptions import InvalidPayloadType, InvalidUser
from src.core.state import GameState
from src.core.types import Payload


class GameStep(BaseModel, ABC):
    game_state: GameState
    local_state: BaseModel

    def validate_payload(self, payload: Payload) -> None:
        """
        Method called by Game.dispatch method.
        :param payload:
        :return:
        """
        if (user := self.game_state.current_user) is not None and user != payload.user:
            raise InvalidUser("User is not permitted to perform action now.")

        if not isinstance(payload, self.payload_class):
            raise InvalidPayloadType(
                f"Expected type '{self.payload_class.__name__}', received {payload.__class__.__name__}"
            )

    def on_start(self) -> GameState:
        """Method called by Game class on next step when step is switched"""

    @abstractmethod
    def dispatch_payload(self, payload: Payload) -> GameState:
        raise NotImplementedError

    @property
    @abstractmethod
    def payload_class(self) -> Type[Payload]:
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def next_step_class(self) -> Type["GameStep"] | None:
        raise NotImplementedError

    @property
    @abstractmethod
    def should_switch_to_next_step(self) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name


class GameStateStore(BaseModel, ABC):
    @abstractmethod
    def save_game_state(self, game_state: GameState) -> Any:
        raise NotImplementedError

    @abstractmethod
    def load_game_state(self) -> GameState:
        raise NotImplementedError


class GameStateAsyncStore(BaseModel, ABC):
    @abstractmethod
    async def save_game_state_async(self, game_state: GameState) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def load_game_state_async(self) -> GameState:
        raise NotImplementedError
