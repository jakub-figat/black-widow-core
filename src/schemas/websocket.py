from typing import Optional

from pydantic import BaseModel, Field

from src.core.cards import Card
from src.core.consts import USER
from src.core.game import GameSettings
from src.schemas.base import BaseSchema
from src.schemas.game import GameModel


class CreateLobbyPayload(BaseSchema):
    max_players: int = Field(..., ge=3, le=4)


class LeaveLobbyPayload(BaseSchema):
    lobby_id: str = Field(..., min_length=8, max_length=40)


class JoinLobbyPayload(BaseSchema):
    lobby_id: str = Field(..., min_length=8, max_length=40)


class GamePreviewSchema(BaseSchema):
    game_id: str
    users: list[str]

    @classmethod
    def from_game(cls, game: GameModel) -> "GamePreviewSchema":
        return cls(game_id=game.game_id, users=game.game.state.users)


class GameDetailState(BaseSchema):
    """Modified version of game state, hides other players' cards"""

    current_user: Optional[USER] = None
    users: list[USER]
    scores: dict[USER, int]
    deck: dict[USER, list[Card]]


class GameDetailStep(BaseSchema):
    local_state: BaseModel


class GameDetailSchema(BaseSchema):
    game_id: str
    game_settings: GameSettings
    users: list[str]
    state: GameDetailState
    current_step: GameDetailState
