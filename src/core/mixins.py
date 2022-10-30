from src.core.cards import CARD_MAPPING
from src.core.enums import CardSuit
from src.core.exceptions import InvalidPayloadBody
from src.core.state import GameState
from src.core.types import RoundPayload
from src.core.utils import check_if_user_has_only_one_suit, check_if_user_has_suit, count_points_for_cards


class RoundPayloadValidationMixin:
    """
    Mixin class providing payload validation logic for InProgressStep and FirstRoundStep.
    """

    def validate_payload(self, payload: RoundPayload) -> None:
        super().validate_payload(payload=payload)
        card = CARD_MAPPING[payload.card]
        if card not in self.game_state.decks[payload.user]:
            raise InvalidPayloadBody(f"User {payload.user} does not have card {payload.card}")

        if card in self.local_state.cards_on_table.values():
            raise InvalidPayloadBody(f"Cannot place card {payload.card}, since it is already on table")

        if card.suit == CardSuit.HEART and not check_if_user_has_only_one_suit(
            deck=self.game_state.decks[payload.user]
        ):
            raise InvalidPayloadBody(
                f"User {payload.user} tried to place heart suit despite having at least one more suit on deck"
            )

        if (suit := self.local_state.table_suit) is not None:
            if card.suit != suit and check_if_user_has_suit(suit=suit, deck=self.game_state.decks[payload.user]):
                raise InvalidPayloadBody(
                    f"Table suit is {suit}, user tries to place {card.suit}," f" despite having matching suit on deck"
                )


class RoundDispatchPayloadMixin:
    """
    Mixin class providing dispatch logic for InProgressStep and FirstRoundStep
    """

    def dispatch_payload(self, payload: RoundPayload) -> GameState:
        card = CARD_MAPPING[payload.card]
        if not self.local_state.cards_on_table:
            self.local_state.table_suit = card.suit

        self.local_state.cards_on_table[payload.user] = card
        new_state = self.game_state.copy(deep=True)
        # TODO: bug, score collecting is wrong if suit does not match
        if len(self.local_state.cards_on_table) == len(self.game_state.users):
            cards_on_table = self.local_state.cards_on_table
            user_collecting_score = max(cards_on_table, key=lambda user: cards_on_table[user].value)
            new_state.scores[user_collecting_score] += count_points_for_cards(deck=cards_on_table.values())
            new_state.current_user = user_collecting_score
            self.local_state.cards_on_table = {}
        else:
            next_user = self.game_state.users[(self.game_state.users.index(payload.user) + 1) % len(new_state.users)]
            new_state.current_user = next_user

        new_state.decks[payload.user].remove(card)
        self.game_state = new_state

        return self.game_state
