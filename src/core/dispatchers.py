from typing import Type

from src.core.abstract import BaseDispatcher
from src.core.exceptions import InvalidPayloadBody
from src.core.types import CardExchangePayload, FinishedPayload, FirstRoundPayload, InProgressPayload, Payload


class CardExchangeDispatcher(BaseDispatcher):
    def validate_payload(self, payload: CardExchangePayload) -> None:
        super().validate_payload(payload=payload)
        for card in payload.cards:
            if card not in self.game_state.decks[payload.user]:
                raise InvalidPayloadBody(f"User {payload.user} does not have card {card.identifier}")

    def dispatch_payload(self, payload: CardExchangePayload) -> None:
        pass

    @property
    def payload_class(self) -> Type[Payload]:
        return CardExchangePayload


class FirstRoundDispatcher(BaseDispatcher):
    def dispatch_payload(self, payload: FirstRoundPayload) -> None:
        pass

    @property
    def payload_class(self) -> Type[Payload]:
        return FirstRoundPayload


class InProgressDispatcher(BaseDispatcher):
    def dispatch_payload(self, payload: InProgressPayload) -> None:
        pass

    @property
    def payload_class(self) -> Type[Payload]:
        return InProgressPayload


class FinishedDispatcher(BaseDispatcher):
    def dispatch_payload(self, payload: FinishedPayload) -> None:
        pass

    @property
    def payload_class(self) -> Type[Payload]:
        return FinishedPayload
