from pydantic import BaseModel, Field

from src.core.cards import Card
from src.core.consts import USER
from src.core.enums import CardSuit


class Payload(BaseModel):
    user: USER


class CardExchangePayload(Payload):
    cards: list[Card] = Field(..., min_items=3, max_items=3, unique_items=True)


class RoundPayload(Payload):
    card: Card


class FinishedPayload(Payload):
    pass


class CardExchangeState(BaseModel):
    cards_to_exchange: dict[USER, list[Card]] = Field(default_factory=dict)


class RoundState(BaseModel):
    cards_on_table: dict[USER, Card] = Field(default_factory=dict)
    table_suit: CardSuit | None = None


class FinishedState(BaseModel):
    users_ready: set = Field(default_factory=set)
