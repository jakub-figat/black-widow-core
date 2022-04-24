from copy import deepcopy
from typing import Type

from src.core.abstract import GameStep
from src.core.cards import Card
from src.core.consts import USER
from src.core.exceptions import InvalidPayloadBody
from src.core.mixins import RoundDispatchPayloadMixin, RoundPayloadValidationMixin
from src.core.state import GameState
from src.core.types import CardExchangePayload, CardExchangeState, Payload, RoundPayload, RoundState
from src.core.utils import get_first_user_card_tuple


class InProgressStep(RoundPayloadValidationMixin, RoundDispatchPayloadMixin, GameStep):
    local_state: RoundState

    def on_start(self) -> None:
        pass

    @property
    def payload_class(self) -> Type[RoundPayload]:
        return RoundPayload

    @property
    def name(self) -> str:
        return "IN_PROGRESS"

    @property
    def next_step_class(self) -> Type["GameStep"] | None:
        pass

    @property
    def should_switch_to_next_step(self) -> bool:
        return not any(self.game_state.decks.values())


class FirstRoundStep(RoundPayloadValidationMixin, RoundDispatchPayloadMixin, GameStep):
    local_state: RoundState

    def on_start(self) -> GameState:
        first_user, card = get_first_user_card_tuple(decks=self.game_state.decks)
        payload = RoundPayload(user=first_user, card=card)
        return self.dispatch_payload(payload=payload)

    @property
    def payload_class(self) -> Type[RoundPayload]:
        return RoundPayload

    @property
    def name(self) -> str:
        return "FIRST_ROUND"

    @property
    def next_step_class(self) -> Type["GameStep"] | None:
        return InProgressStep

    @property
    def should_switch_to_next_step(self) -> bool:
        return not self.local_state.cards_on_table


class CardExchangeStep(GameStep):
    local_state: CardExchangeState

    def validate_payload(self, payload: CardExchangePayload) -> None:
        super().validate_payload(payload=payload)
        if payload.user in self.local_state:
            raise InvalidPayloadBody(f"User {payload.user} has already declared cards for exchange")

        for card in payload.cards:
            if card not in self.game_state.decks[payload.user]:
                raise InvalidPayloadBody(f"User {payload.user} does not have card {card}")

    def dispatch_payload(self, payload: CardExchangePayload) -> GameState:
        self.local_state.cards_to_exchange[payload.user] = payload.cards
        if len(self.local_state.cards_to_exchange) == len(self.game_state.users):
            new_state = self.game_state.copy(deep=True)
            new_state.decks = self._get_decks_with_cards_exchanged()
            self.local_state.cards_to_exchange = {}
            self.game_state = new_state

        return self.game_state

    def _get_decks_with_cards_exchanged(self) -> dict[USER, list[Card]]:
        new_decks = deepcopy(self.game_state.decks)
        users = self.game_state.users

        # if users: [1, 2, 3] then: {1: 2, 2: 3, 3:1}
        from_to_mapping = {user: users[index % len(users)] for index, user in enumerate(users, start=1)}

        for user, cards_to_exchange in self.local_state.cards_to_exchange.items():
            for card in cards_to_exchange:
                new_decks[user].remove(card)
                new_decks[from_to_mapping[user]].append(card)

        return new_decks

    def on_start(self) -> None:
        pass

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
