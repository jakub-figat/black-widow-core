import logging

from pydantic import BaseModel, Field

from src.core.abstract import GameStateAsyncStore, GameStateStore, GameStep
from src.core.consts import USER
from src.core.state import GameState
from src.core.steps import CardExchangeStep
from src.core.types import CardExchangeState, Payload


class GameSettings(BaseModel):
    max_score: int = Field(default=100, gt=0)
    timeout: int = Field(default=60, gt=30)


class Game(BaseModel):
    settings: GameSettings
    state: GameState
    current_step: GameStep
    store: GameStateStore | GameStateAsyncStore

    @classmethod
    def start_game(
        cls,
        users: list[USER],
        store: GameStateStore | GameStateAsyncStore,
        max_score: int = 100,
    ) -> "Game":
        settings = GameSettings(max_score=max_score)
        state = GameState.get_initial_game_state(users=users)
        step = CardExchangeStep(game_state=state, local_state=CardExchangeState())
        return cls(state=state, settings=settings, store=store, current_step=step)

    def dispatch(self, payload: Payload) -> None:
        game_step = self.state.current_step
        game_step.validate_payload(payload=payload)
        self.state = game_step.dispatch_payload(payload=payload)

        if self.is_finished:
            logging.info("Game finished")
            return

        if game_step.should_switch_to_next_step:
            next_step_class = self.current_step.next_step_class or CardExchangeStep
            self.state.current_step = next_step_class(game_state=self.state)
            self.state = self.current_step.on_start()

    def _load_state(self) -> None:
        self.state = self.store.load_game_state()

    def _save_state(self) -> None:
        self.store.save_game_state(game_state=self.state)

    async def _load_state_async(self) -> None:
        self.state = await self.store.load_game_state_async()

    async def _save_state_async(self) -> None:
        await self.store.save_game_state_async(game_state=self.state)

    @property
    def is_finished(self) -> bool:
        return self.current_step is None and max(self.state.scores.values()) >= self.settings.max_score
