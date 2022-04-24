from enum import Enum


class CardSuit(str, Enum):
    SPADE = "SPADE"
    CLUB = "CLUB"
    HEART = "HEART"
    DIAMOND = "DIAMOND"
