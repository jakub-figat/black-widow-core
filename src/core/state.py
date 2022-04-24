from pydantic import BaseModel

from src.core.cards import Card
from src.core.consts import USER
from src.core.utils import get_initial_decks, get_initial_scores


class GameState(BaseModel):
    current_user: USER | None = None
    users: list[USER]
    scores: dict[USER, int]
    decks: dict[USER, list[Card]]

    @classmethod
    def get_initial_game_state(cls, users: list[USER]) -> "GameState":
        return cls(
            users=users,
            decks=get_initial_decks(users),
            scores=get_initial_scores(users),
        )

    @classmethod
    def from_state(cls, game_state: "GameState") -> "GameState":
        return cls(
            users=game_state.users,
            scores=game_state.scores,
            decks=get_initial_decks(users=game_state.users),
        )
