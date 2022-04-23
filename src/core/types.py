from pydantic import BaseModel, Field

from src.core import cards
from src.core.consts import USER


class Payload(BaseModel):
    user: USER


class CardExchangePayload(Payload):
    cards: list[cards.Card] = Field(..., min_items=3, max_items=3, unique_items=True)


class CardExchangeState(BaseModel):
    cards_to_exchange: dict[USER, list[cards.Card]] = Field(default_factory=dict)


class FirstRoundPayload(Payload):
    pass


class InProgressPayload(Payload):
    pass


class FinishedPayload(Payload):
    pass
