from enum import Enum


class GameStep(str, Enum):
    CARD_EXCHANGE = "CARD_EXCHANGE"
    FIRST_ROUND = "FIRST_ROUND"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"
