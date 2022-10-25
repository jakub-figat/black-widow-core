from pydantic import Field

from src.schemas.base import BaseSchema


class CreateLobbyPayload(BaseSchema):
    max_players: int = Field(..., ge=3, le=4)


class LeaveLobbyPayload(BaseSchema):
    lobby_id: str = Field(..., min_length=8, max_length=40)


class JoinLobbyPayload(BaseSchema):
    lobby_id: str = Field(..., min_length=8, max_length=40)
