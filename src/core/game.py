from typing import Type

from pydantic import BaseModel, Field

from src.core.abstract import BaseDispatcher, GameStateAsyncStore, GameStateStore
from src.core.cards import Card
from src.core.consts import USER
from src.core.dispatchers import CardExchangeDispatcher, FinishedDispatcher, FirstRoundDispatcher, InProgressDispatcher
from src.core.enums import GameStep
from src.core.types import Payload
from src.core.utils import get_initial_decks, get_initial_scores


class GameSettings(BaseModel):
    max_score: int = Field(default=100, gt=0)
    timeout: int = Field(default=60, gt=30)


class GameState(BaseModel):
    current_step: GameStep
    current_user: USER | None = None
    users: list[USER]
    scores: dict[USER, int]
    decks: dict[USER, list[Card]]

    @classmethod
    def get_initial_game_state(cls, users: list[USER]) -> "GameState":
        return cls(
            current_step=GameStep.CARD_EXCHANGE,
            users=users,
            decks=get_initial_decks(users),
            scores=get_initial_scores(users),
        )


class Game(BaseModel):
    state: GameState
    store: GameStateStore | GameStateAsyncStore
    settings: GameSettings
    dispatcher_mapping: dict[GameStep, Type[BaseDispatcher]] = {
        GameStep.CARD_EXCHANGE: CardExchangeDispatcher,
        GameStep.FIRST_ROUND: FirstRoundDispatcher,
        GameStep.IN_PROGRESS: InProgressDispatcher,
        GameStep.FINISHED: FinishedDispatcher,
    }

    @classmethod
    def start_game(
        cls, users: list[USER], store: GameStateStore | GameStateAsyncStore, max_score: int = 100
    ) -> "Game":
        settings = GameSettings(max_score=max_score)
        state = GameState.get_initial_game_state(users=users)
        return cls(state=state, settings=settings, store=store)

    def dispatch(self, payload: Payload) -> None:
        dispatcher = self.dispatcher_mapping[self.state.current_step](game_state=self.state)
        dispatcher.validate_payload(payload=payload)
        self.state = dispatcher.dispatch_payload(payload=payload)

    def _load_state(self) -> None:
        self.state = self.store.load_game_state()

    def _save_state(self) -> None:
        self.store.save_game_state(game_state=self.state)

    async def _load_state_async(self) -> None:
        self.state = await self.store.load_game_state_async()

    async def _save_state_async(self) -> None:
        await self.store.save_game_state_async(game_state=self.state)
