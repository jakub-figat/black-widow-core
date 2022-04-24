from pydantic import BaseModel, Field

from src.core.enums import CardSuit
from src.core.exceptions import InvalidCardComparison


class Card(BaseModel):
    suit: CardSuit
    value: int = Field(..., ge=2, le=14)
    score: int = 0

    def __lt__(self, card: "Card") -> bool:
        if self.suit != card.suit:
            raise InvalidCardComparison("Cannot compare card values with different suits.")

        return self.value < card.value

    def __gt__(self, card: "Card") -> bool:
        if self.suit != card.suit:
            raise InvalidCardComparison("Cannot compare card values with different suits.")

        return self.value > card.value

    def __str__(self) -> str:
        return f"{self.suit}_{self.value}"


SPADE_2 = Card(suit=CardSuit.SPADE, value=2)
SPADE_3 = Card(suit=CardSuit.SPADE, value=3)
SPADE_4 = Card(suit=CardSuit.SPADE, value=4)
SPADE_5 = Card(suit=CardSuit.SPADE, value=5)
SPADE_6 = Card(suit=CardSuit.SPADE, value=6)
SPADE_7 = Card(suit=CardSuit.SPADE, value=7)
SPADE_8 = Card(suit=CardSuit.SPADE, value=8)
SPADE_9 = Card(suit=CardSuit.SPADE, value=9)
SPADE_10 = Card(suit=CardSuit.SPADE, value=10)
SPADE_JACK = Card(suit=CardSuit.SPADE, value=11)
SPADE_QUEEN = Card(suit=CardSuit.SPADE, value=12, score=13)
SPADE_KING = Card(suit=CardSuit.SPADE, value=13, score=10)
SPADE_ACE = Card(suit=CardSuit.SPADE, value=14, score=7)

CLUB_2 = Card(suit=CardSuit.CLUB, value=2)
CLUB_3 = Card(suit=CardSuit.CLUB, value=3)
CLUB_4 = Card(suit=CardSuit.CLUB, value=4)
CLUB_5 = Card(suit=CardSuit.CLUB, value=5)
CLUB_6 = Card(suit=CardSuit.CLUB, value=6)
CLUB_7 = Card(suit=CardSuit.CLUB, value=7)
CLUB_8 = Card(suit=CardSuit.CLUB, value=8)
CLUB_9 = Card(suit=CardSuit.CLUB, value=9)
CLUB_10 = Card(suit=CardSuit.CLUB, value=10)
CLUB_JACK = Card(suit=CardSuit.CLUB, value=11)
CLUB_QUEEN = Card(suit=CardSuit.CLUB, value=12)
CLUB_KING = Card(suit=CardSuit.CLUB, value=13)
CLUB_ACE = Card(suit=CardSuit.CLUB, value=14)

DIAMOND_2 = Card(suit=CardSuit.DIAMOND, value=2)
DIAMOND_3 = Card(suit=CardSuit.DIAMOND, value=3)
DIAMOND_4 = Card(suit=CardSuit.DIAMOND, value=4)
DIAMOND_5 = Card(suit=CardSuit.DIAMOND, value=5)
DIAMOND_6 = Card(suit=CardSuit.DIAMOND, value=6)
DIAMOND_7 = Card(suit=CardSuit.DIAMOND, value=7)
DIAMOND_8 = Card(suit=CardSuit.DIAMOND, value=8)
DIAMOND_9 = Card(suit=CardSuit.DIAMOND, value=9)
DIAMOND_10 = Card(suit=CardSuit.DIAMOND, value=10)
DIAMOND_JACK = Card(suit=CardSuit.DIAMOND, value=11)
DIAMOND_QUEEN = Card(suit=CardSuit.DIAMOND, value=12)
DIAMOND_KING = Card(suit=CardSuit.DIAMOND, value=13)
DIAMOND_ACE = Card(suit=CardSuit.DIAMOND, value=14)

HEART_2 = Card(suit=CardSuit.HEART, value=2, score=1)
HEART_3 = Card(suit=CardSuit.HEART, value=3, score=1)
HEART_4 = Card(suit=CardSuit.HEART, value=4, score=1)
HEART_5 = Card(suit=CardSuit.HEART, value=5, score=1)
HEART_6 = Card(suit=CardSuit.HEART, value=6, score=1)
HEART_7 = Card(suit=CardSuit.HEART, value=7, score=1)
HEART_8 = Card(suit=CardSuit.HEART, value=8, score=1)
HEART_9 = Card(suit=CardSuit.HEART, value=9, score=1)
HEART_10 = Card(suit=CardSuit.HEART, value=10, score=1)
HEART_JACK = Card(suit=CardSuit.HEART, value=11, score=1)
HEART_QUEEN = Card(suit=CardSuit.HEART, value=12, score=1)
HEART_KING = Card(suit=CardSuit.HEART, value=13, score=1)
HEART_ACE = Card(suit=CardSuit.HEART, value=14, score=1)


ALL_CARDS = [
    SPADE_2,
    SPADE_3,
    SPADE_4,
    SPADE_5,
    SPADE_6,
    SPADE_7,
    SPADE_8,
    SPADE_9,
    SPADE_10,
    SPADE_JACK,
    SPADE_QUEEN,
    SPADE_KING,
    SPADE_ACE,
    CLUB_2,
    CLUB_3,
    CLUB_4,
    CLUB_5,
    CLUB_6,
    CLUB_7,
    CLUB_8,
    CLUB_9,
    CLUB_10,
    CLUB_JACK,
    CLUB_QUEEN,
    CLUB_KING,
    CLUB_ACE,
    DIAMOND_2,
    DIAMOND_3,
    DIAMOND_4,
    DIAMOND_5,
    DIAMOND_6,
    DIAMOND_7,
    DIAMOND_8,
    DIAMOND_9,
    DIAMOND_10,
    DIAMOND_JACK,
    DIAMOND_QUEEN,
    DIAMOND_KING,
    DIAMOND_ACE,
    HEART_2,
    HEART_3,
    HEART_4,
    HEART_5,
    HEART_6,
    HEART_7,
    HEART_8,
    HEART_9,
    HEART_10,
    HEART_JACK,
    HEART_QUEEN,
    HEART_KING,
    HEART_ACE,
]
