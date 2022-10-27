from typing import Any, Optional

from pydantic import BaseModel, Field

from src.core.cards import Card
from src.core.consts import USER
from src.core.game import Game, GameSettings
from src.core.steps import STEP_MAPPING, CardExchangeStep
from src.core.types import CardExchangeState
from src.schemas.base import BaseSchema
from src.schemas.game import GameModel


class CreateLobbyPayload(BaseSchema):
    max_players: int = Field(..., ge=3, le=4)


class LeaveLobbyPayload(BaseSchema):
    lobby_id: str = Field(..., min_length=36, max_length=36)


class JoinLobbyPayload(BaseSchema):
    lobby_id: str = Field(..., min_length=36, max_length=36)


class GetGameDetailPayload(BaseSchema):
    game_id: str = Field(..., min_length=36, max_length=36)


class MakeMovePayload(BaseSchema):
    game_id: str = Field(..., min_length=36, max_length=36)
    game_payload: dict[str, Any]


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
    deck: list[Card]


class GameDetailStep(BaseSchema):
    local_state: BaseModel


class GameDetailSchema(BaseSchema):
    game_id: str
    game_settings: GameSettings
    state: GameDetailState
    current_step: GameDetailStep

    @classmethod
    def from_game(cls, game: GameModel, user_id: str) -> "GameDetailSchema":
        state_dict = game.game.state.dict()
        state_dict["deck"] = state_dict.pop("decks")[user_id]
        obfuscated_state = GameDetailState(**state_dict)

        obfuscated_step = None
        if isinstance(STEP_MAPPING[game.game_step], CardExchangeStep):
            local_state_dict = game.game.current_step.local_state.dict()
            local_state_dict["cards_to_exchange"] = local_state_dict.pop("cards_to_exchange")[user_id]
            obfuscated_step = GameDetailStep(local_state=CardExchangeState(**local_state_dict))

        return cls(
            game_id=game.game_id,
            game_settings=game.game.settings,
            state=obfuscated_state,
            current_step=obfuscated_step or game.game.current_step,
        )
