"""
FirstRoundStep and InProgress Step share almost all logic, so their test cases are unified.
Differences between their logic will be tested in integration tests.
"""
import pytest

from src.core import cards
from src.core.enums import CardSuit
from src.core.exceptions import InvalidPayloadBody
from src.core.state import GameState
from src.core.steps import FirstRoundStep, InProgressStep
from src.core.types import RoundPayload, RoundState
from src.core.utils import get_initial_scores


@pytest.fixture
def game_state_with_first_round() -> GameState:
    return GameState(
        users=["user_1", "user_2", "user_3", "user_4"],
        scores=get_initial_scores(users=["user_1", "user_2", "user_3", "user_4"]),
        decks={
            "user_1": [cards.HEART_4, cards.HEART_5, cards.DIAMOND_3],
            "user_2": [cards.CLUB_2, cards.CLUB_3, cards.CLUB_4, cards.HEART_QUEEN],
            "user_3": [cards.HEART_QUEEN, cards.HEART_KING],
            "user_4": [cards.DIAMOND_3, cards.DIAMOND_4, cards.DIAMOND_5],
        },
    )


@pytest.fixture
def game_state_with_current_player() -> GameState:
    return GameState(
        users=["user_1", "user_2", "user_3", "user_4"],
        scores=get_initial_scores(users=["user_1", "user_2", "user_3", "user_4"]),
        decks={
            "user_1": [cards.HEART_4, cards.HEART_5, cards.DIAMOND_6],
            "user_2": [cards.CLUB_2, cards.CLUB_3, cards.CLUB_4, cards.HEART_7],
            "user_3": [cards.HEART_QUEEN, cards.HEART_KING],
            "user_4": [cards.DIAMOND_3, cards.DIAMOND_4, cards.DIAMOND_5],
        },
        current_user="user_3",
    )


@pytest.fixture
def game_state_with_current_player_round_when_everyone_has_one_suit() -> GameState:
    return GameState(
        users=["user_1", "user_2", "user_3", "user_4"],
        scores=get_initial_scores(users=["user_1", "user_2", "user_3", "user_4"]),
        decks={
            "user_1": [cards.SPADE_QUEEN],
            "user_2": [cards.SPADE_KING],
            "user_3": [cards.SPADE_4],
            "user_4": [cards.SPADE_JACK],
        },
        current_user="user_3",
    )


@pytest.mark.parametrize(
    "payload,local_state",
    [
        (RoundPayload(user="user_1", card=cards.SPADE_5), RoundState()),  # user does not have a card
        (
            RoundPayload(user="user_2", card=cards.CLUB_4),
            RoundState(cards_on_table={"user_2": cards.CLUB_4}),
        ),  # card is already on table
        (
            RoundPayload(user="user_2", card=cards.CLUB_3),
            RoundState(cards_on_table={"user_1": cards.HEART_4}, table_suit=CardSuit.HEART),
        ),  # suit does not match table's suit
        (
            RoundPayload(user="user_1", card=cards.HEART_5),
            RoundState(),
        ),  # user tries to put heart while having other suits in deck
    ],
)
def test_validate_payload_raises_error_on_invalid_payload(
    payload: RoundPayload, local_state: RoundState, game_state_with_first_round: GameState
) -> None:
    step = FirstRoundStep(game_state=game_state_with_first_round, local_state=local_state)
    with pytest.raises(InvalidPayloadBody):
        step.validate_payload(payload=payload)


def test_first_round_step_on_start_method(game_state_with_first_round: GameState) -> None:
    step = FirstRoundStep(game_state=game_state_with_first_round, local_state=RoundState())
    new_state = step.on_start()

    assert new_state != game_state_with_first_round
    assert step.local_state.table_suit == CardSuit.CLUB
    assert step.local_state.cards_on_table == {"user_2": cards.CLUB_2}
    assert new_state.decks == {
        "user_1": [cards.HEART_4, cards.HEART_5, cards.DIAMOND_3],
        "user_2": [cards.CLUB_3, cards.CLUB_4, cards.HEART_QUEEN],
        "user_3": [cards.HEART_QUEEN, cards.HEART_KING],
        "user_4": [cards.DIAMOND_3, cards.DIAMOND_4, cards.DIAMOND_5],
    }
    assert new_state.current_user == "user_3"
    assert not step.should_switch_to_next_step


def test_dispatch_payload_when_first_card_is_on_table(game_state_with_first_round: GameState) -> None:
    step = FirstRoundStep(game_state=game_state_with_first_round, local_state=RoundState())
    step.on_start()
    new_state = step.dispatch_payload(payload=RoundPayload(user="user_3", card=cards.HEART_QUEEN))

    assert new_state != game_state_with_first_round
    assert step.local_state.table_suit == CardSuit.CLUB
    assert step.local_state.cards_on_table == {"user_2": cards.CLUB_2, "user_3": cards.HEART_QUEEN}
    assert new_state.decks == {
        "user_1": [cards.HEART_4, cards.HEART_5, cards.DIAMOND_3],
        "user_2": [cards.CLUB_3, cards.CLUB_4, cards.HEART_QUEEN],
        "user_3": [cards.HEART_KING],
        "user_4": [cards.DIAMOND_3, cards.DIAMOND_4, cards.DIAMOND_5],
    }
    assert new_state.current_user == "user_4"
    assert not step.should_switch_to_next_step


def test_dispatch_payload_when_last_card_is_being_put(game_state_with_current_player: GameState) -> None:
    step = InProgressStep(game_state=game_state_with_current_player, local_state=RoundState())

    step.dispatch_payload(payload=RoundPayload(user="user_3", card=cards.HEART_QUEEN))
    step.dispatch_payload(payload=RoundPayload(user="user_4", card=cards.DIAMOND_3))
    step.dispatch_payload(payload=RoundPayload(user="user_1", card=cards.HEART_5))
    new_state = step.dispatch_payload(payload=RoundPayload(user="user_2", card=cards.HEART_7))

    assert new_state != game_state_with_current_player
    assert step.local_state.table_suit == CardSuit.HEART
    assert not step.local_state.cards_on_table
    assert new_state.decks == {
        "user_1": [cards.HEART_4, cards.DIAMOND_6],
        "user_2": [cards.CLUB_2, cards.CLUB_3, cards.CLUB_4],
        "user_3": [cards.HEART_KING],
        "user_4": [cards.DIAMOND_4, cards.DIAMOND_5],
    }
    assert new_state.current_user == "user_3"
    assert new_state.scores == {"user_1": 0, "user_2": 0, "user_3": 3, "user_4": 0}
    assert not step.should_switch_to_next_step


def test_dispatch_payload_when_everyone_has_card_of_given_suit(
    game_state_with_current_player_round_when_everyone_has_one_suit: GameState,
) -> None:
    step = InProgressStep(
        game_state=game_state_with_current_player_round_when_everyone_has_one_suit, local_state=RoundState()
    )

    step.dispatch_payload(payload=RoundPayload(user="user_3", card=cards.SPADE_4))
    step.dispatch_payload(payload=RoundPayload(user="user_4", card=cards.SPADE_JACK))
    step.dispatch_payload(payload=RoundPayload(user="user_1", card=cards.SPADE_QUEEN))
    new_state = step.dispatch_payload(payload=RoundPayload(user="user_2", card=cards.SPADE_KING))

    assert new_state != game_state_with_current_player_round_when_everyone_has_one_suit
    assert step.local_state.table_suit == CardSuit.SPADE
    assert not step.local_state.cards_on_table
    assert new_state.decks == {
        "user_1": [],
        "user_2": [],
        "user_3": [],
        "user_4": [],
    }
    assert new_state.current_user == "user_2"
    assert new_state.scores == {"user_1": 0, "user_2": 23, "user_3": 0, "user_4": 0}
    assert step.should_switch_to_next_step
