from pydantic import BaseModel

from src.core.consts import USER


class Payload(BaseModel):
    user: USER


class CardExchangePayload(Payload):
    pass


class FirstRoundPayload(Payload):
    pass


class InProgressPayload(Payload):
    pass


class FinishedPayload(Payload):
    pass
