from typing import Optional

from pydantic import BaseModel, Field, validator

from src.core.cards import CARD_MAPPING, Card
from src.core.consts import USER
from src.core.enums import CardSuit


class Payload(BaseModel):
    user: USER


class CardExchangePayload(Payload):
    cards: list[str] = Field(..., min_items=3, max_items=3, unique_items=True)

    @validator("cards")
    def validate_cards(cls, cards: list[str]) -> list[str]:
        for card in cards:
            if card not in CARD_MAPPING:
                raise ValueError(f"{card} is not a valid card")

        return cards


class RoundPayload(Payload):
    card: str

    @validator("card")
    def validate_card(cls, card: str) -> str:
        if card not in CARD_MAPPING:
            raise ValueError(f"{card} is not a valid card")

        return card


class FinishedPayload(Payload):
    pass


class CardExchangeState(BaseModel):
    cards_to_exchange: dict[USER, list[Card]] = Field(default_factory=dict)


class RoundState(BaseModel):
    cards_on_table: dict[USER, Card] = Field(default_factory=dict)
    table_suit: Optional[CardSuit] = None


class FinishedState(BaseModel):
    users_ready: set = Field(default_factory=set)
