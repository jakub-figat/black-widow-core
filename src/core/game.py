import logging
from typing import Union

from pydantic import BaseModel, Field

from src.core.abstract import GameStateAsyncStore, GameStateStore, GameStep
from src.core.consts import USER
from src.core.exceptions import NoStoreSet
from src.core.state import GameState
from src.core.steps import CardExchangeStep, FinishedStep
from src.core.types import Payload


class GameSettings(BaseModel):
    max_score: int = Field(default=100, gt=0)
    timeout: int = Field(default=60, gt=30)


class Game(BaseModel):
    settings: GameSettings
    state: GameState
    current_step: GameStep
    store: Union[GameStateStore, GameStateAsyncStore, None] = None

    @classmethod
    def start_game(
        cls,
        users: list[USER],
        store: Union[GameStateStore, GameStateAsyncStore, None] = None,
        max_score: int = 100,
    ) -> "Game":
        settings = GameSettings(max_score=max_score)
        state = GameState.get_initial_game_state(users=users)
        step = CardExchangeStep(game_state=state)
        return cls(state=state, settings=settings, store=store, current_step=step)

    def dispatch(self, payload: Payload) -> None:
        if self.is_finished:
            logging.info("Game finished.")
            return

        game_step = self.current_step
        game_step.validate_payload(payload=payload)
        self.state = game_step.dispatch_payload(payload=payload)

        if game_step.should_switch_to_next_step:
            next_step_class = self.current_step.next_step_class or CardExchangeStep
            self.current_step = next_step_class(game_state=self.state)
            self.state = self.current_step.on_start()

    def _load_state(self) -> None:
        if self.store is None:
            raise NoStoreSet("No store set")
        self.state = self.store.load_game_state()

    def _save_state(self) -> None:
        if self.store is None:
            raise NoStoreSet("No store set")
        self.store.save_game_state(game_state=self.state)

    async def _load_state_async(self) -> None:
        if self.store is None:
            raise NoStoreSet("No store set")
        self.state = await self.store.load_game_state_async()

    async def _save_state_async(self) -> None:
        if self.store is None:
            raise NoStoreSet("No store set")
        await self.store.save_game_state_async(game_state=self.state)

    @property
    def is_finished(self) -> bool:
        return (
            isinstance(self.current_step, FinishedStep) and max(self.state.scores.values()) >= self.settings.max_score
        )
