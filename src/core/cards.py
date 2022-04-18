from pydantic import BaseModel


class Card(BaseModel):
    identifier: str

    def __lt__(self, card: "Card") -> bool:
        name, value = self.identifier.split("_")
        other_name, other_value = self.identifier.split("_")

        if name != other_name:
            raise ValueError("Cannot compare card values with different suits.")

        return value < other_value

    def __gt__(self, card: "Card") -> bool:
        name, value = self.identifier.split("_")
        other_name, other_value = self.identifier.split("_")

        if name != other_name:
            raise ValueError("Cannot compare card values with different suits.")

        return value > other_value


SPADE_2 = Card(identifier="SPADE_2")
SPADE_3 = Card(identifier="SPADE_3")
SPADE_4 = Card(identifier="SPADE_4")
SPADE_5 = Card(identifier="SPADE_5")
SPADE_6 = Card(identifier="SPADE_6")
SPADE_7 = Card(identifier="SPADE_7")
SPADE_8 = Card(identifier="SPADE_8")
SPADE_9 = Card(identifier="SPADE_9")
SPADE_10 = Card(identifier="SPADE_10")
SPADE_JACK = Card(identifier="SPADE_11")
SPADE_QUEEN = Card(identifier="SPADE_12")
SPADE_KING = Card(identifier="SPADE_13")
SPADE_ACE = Card(identifier="SPADE_14")

CLUB_2 = Card(identifier="CLUB_2")
CLUB_3 = Card(identifier="CLUB_3")
CLUB_4 = Card(identifier="CLUB_4")
CLUB_5 = Card(identifier="CLUB_5")
CLUB_6 = Card(identifier="CLUB_6")
CLUB_7 = Card(identifier="CLUB_7")
CLUB_8 = Card(identifier="CLUB_8")
CLUB_9 = Card(identifier="CLUB_9")
CLUB_10 = Card(identifier="CLUB_10")
CLUB_JACK = Card(identifier="CLUB_11")
CLUB_QUEEN = Card(identifier="CLUB_12")
CLUB_KING = Card(identifier="CLUB_13")
CLUB_ACE = Card(identifier="CLUB_14")

DIAMOND_2 = Card(identifier="DIAMOND_2")
DIAMOND_3 = Card(identifier="DIAMOND_3")
DIAMOND_4 = Card(identifier="DIAMOND_4")
DIAMOND_5 = Card(identifier="DIAMOND_5")
DIAMOND_6 = Card(identifier="DIAMOND_6")
DIAMOND_7 = Card(identifier="DIAMOND_7")
DIAMOND_8 = Card(identifier="DIAMOND_8")
DIAMOND_9 = Card(identifier="DIAMOND_9")
DIAMOND_10 = Card(identifier="DIAMOND_10")
DIAMOND_JACK = Card(identifier="DIAMOND_11")
DIAMOND_QUEEN = Card(identifier="DIAMOND_12")
DIAMOND_KING = Card(identifier="DIAMOND_13")
DIAMOND_ACE = Card(identifier="DIAMOND_14")

HEART_2 = Card(identifier="HEART_2")
HEART_3 = Card(identifier="HEART_3")
HEART_4 = Card(identifier="HEART_4")
HEART_5 = Card(identifier="HEART_5")
HEART_6 = Card(identifier="HEART_6")
HEART_7 = Card(identifier="HEART_7")
HEART_8 = Card(identifier="HEART_8")
HEART_9 = Card(identifier="HEART_9")
HEART_10 = Card(identifier="HEART_10")
HEART_JACK = Card(identifier="HEART_11")
HEART_QUEEN = Card(identifier="HEART_12")
HEART_KING = Card(identifier="HEART_13")
HEART_ACE = Card(identifier="HEART_14")


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
