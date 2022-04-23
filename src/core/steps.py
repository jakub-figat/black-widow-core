from typing import TYPE_CHECKING, Type

from src.core.abstract import GameStep
from src.core.cards import Card
from src.core.consts import USER
from src.core.exceptions import InvalidPayloadBody
from src.core.types import CardExchangePayload, CardExchangeState, FirstRoundPayload, Payload


if TYPE_CHECKING:
    from src.core.game import GameState


class FirstRoundStep(GameStep):
    def validate_payload(self, payload: FirstRoundPayload) -> None:
        pass

    def dispatch_payload(self, payload: Payload) -> "GameState":
        pass

    @property
    def payload_class(self) -> Type[Payload]:
        return FirstRoundPayload

    @property
    def name(self) -> str:
        return "FIRST_ROUND"

    @property
    def next_step_class(self) -> Type["GameStep"] | None:
        return None

    @property
    def should_switch_to_next_step(self) -> bool:
        pass


class CardExchangeStep(GameStep):
    local_state: CardExchangeState

    def validate_payload(self, payload: CardExchangePayload) -> None:
        super().validate_payload(payload=payload)
        if payload.user in self.local_state:
            raise InvalidPayloadBody(f"User {payload.user} has already declared cards for exchange")

        for card in payload.cards:
            if card not in self.game_state.decks[payload.user]:
                raise InvalidPayloadBody(f"User {payload.user} does not have card {card.identifier}")

    def dispatch_payload(self, payload: CardExchangePayload) -> "GameState":
        self.local_state.cards_to_exchange[payload.user] = payload.cards
        if len(self.local_state) == len(self.game_state.users):
            new_state = self.game_state.copy(deep=True)
            new_state.decks = self._get_decks_with_cards_exchanged()

        return self.game_state

    def _get_decks_with_cards_exchanged(self) -> dict[USER, list[Card]]:
        new_decks = self.game_state.decks[:]
        users = self.game_state.users

        # if users: [1, 2, 3] then: {1: 2, 2: 3, 3:1}
        from_to_mapping = {user: users[index % len(users)] for user, index in enumerate(users, start=1)}

        for user, cards_to_exchange in self.local_state.cards_to_exchange.items():
            for card in cards_to_exchange:
                new_decks[user].remove(card)
                new_decks[from_to_mapping[user]].append(card)

        return new_decks

    @property
    def payload_class(self) -> Type[Payload]:
        return CardExchangePayload

    @property
    def name(self) -> str:
        return "CARD_EXCHANGE"

    @property
    def next_step_class(self) -> Type["GameStep"] | None:
        return FirstRoundStep

    @property
    def should_switch_to_next_step(self) -> bool:
        return not self.local_state.cards_to_exchange
