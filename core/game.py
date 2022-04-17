from typing import Type

from pydantic import BaseModel, Field

from core.abstract import GameStateStore, GameStep
from core.enums import Cards


class GameSettings(BaseModel):
    max_players: int = Field(default=4, gt=3, le=4)
    max_score: int = Field(default=100, gt=0)


class GameState(BaseModel):
    current_step: Type[GameStep]
    current_player: str
    players: list[str]
    score: dict[str, int]
    decks: dict[str, list[Cards]]


class Game(BaseModel):
    state: GameState
    settings: GameSettings
    store: GameStateStore

    def _load_state(self) -> None:
        self.state = self.store.load_game_state()

    def _save_state(self) -> None:
        self.store.save_game_state(game_state=self.state)
