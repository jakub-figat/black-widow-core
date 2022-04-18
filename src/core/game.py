from typing import Type

from pydantic import BaseModel, Field

from src.core.abstract import GameStateAsyncStore, GameStateStore
from src.core.cards import Card
from src.core.consts import USER
from src.core.enums import GameStep
from src.core.utils import get_initial_game_state


class GameSettings(BaseModel):
    max_score: int = Field(default=100, gt=0)
    timeout: int = Field(default=60, gt=30)


class GameState(BaseModel):
    current_step: GameStep
    current_player: USER | None = None
    users: list[USER]
    scores: dict[USER, int]
    decks: dict[USER, list[Card]]


class Game(BaseModel):
    state: GameState
    store: GameStateStore | GameStateAsyncStore
    settings: GameSettings

    @classmethod
    def start_game(
        cls, users: list[USER], store: GameStateStore | GameStateAsyncStore, max_score: int = 100
    ) -> "Game":
        settings = GameSettings(max_score=max_score)
        state = get_initial_game_state(users=users)

        return cls(state=state, settings=settings, store=store)

    def _load_state(self) -> None:
        self.state = self.store.load_game_state()

    def _save_state(self) -> None:
        self.store.save_game_state(game_state=self.state)

    async def _load_state_async(self) -> None:
        self.state = await self.store.load_game_state_async()

    async def _save_state_async(self) -> None:
        await self.store.save_game_state_async(game_state=self.state)
