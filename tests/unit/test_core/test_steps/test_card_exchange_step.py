import pytest

from src.core.exceptions import InvalidPayloadBody
from src.core.game import GameState
from src.core.steps import CardExchangePayload, CardExchangeState, CardExchangeStep


@pytest.fixture
def initial_game_state_with_three_users() -> GameState:
    return GameState.get_initial_game_state(users=["user_1", "user_2", "user_3"])


@pytest.fixture
def initial_game_state_with_four_users() -> GameState:
    return GameState.get_initial_game_state(users=["user_1", "user_2", "user_3", "user_4"])


def test_validate_payload(initial_game_state_with_four_users: GameState) -> None:
    step = CardExchangeStep(game_state=initial_game_state_with_four_users, local_state=CardExchangeState())
    decks = initial_game_state_with_four_users.decks
    payload = CardExchangePayload(user="user_1", cards=decks["user_1"][:2] + decks["user_2"][:1])
    with pytest.raises(InvalidPayloadBody):
        step.validate_payload(payload=payload)


def test_dispatch_payload() -> None:
    pass


def test_get_decks_with_cards_exchanged() -> None:
    pass


def test_should_switch_to_next_step() -> None:
    pass
