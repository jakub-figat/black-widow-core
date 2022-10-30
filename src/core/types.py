from typing import Optional

from pydantic import Field, validator

from src.core.cards import CARD_MAPPING, Card
from src.core.consts import USER
from src.core.enums import CardSuit
from src.core.schemas import BaseSchema


class Payload(BaseSchema):
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


class CardExchangeState(BaseSchema):
    cards_to_exchange: dict[USER, list[Card]] = Field(default_factory=dict)


class RoundState(BaseSchema):
    cards_on_table: dict[USER, Card] = Field(default_factory=dict)
    table_suit: Optional[CardSuit] = None


class FinishedState(BaseSchema):
    users_ready: list[str] = Field(default_factory=list)
