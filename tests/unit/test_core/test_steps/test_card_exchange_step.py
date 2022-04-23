import pytest

from src.core.cards import DIAMOND_2, DIAMOND_3, DIAMOND_4, HEART_2, HEART_3, HEART_4, SPADE_2, SPADE_3, SPADE_4, Card
from src.core.consts import USER
from src.core.exceptions import InvalidPayloadBody
from src.core.game import GameState
from src.core.steps import CardExchangePayload, CardExchangeState, CardExchangeStep
from src.utils import is_list_contained_by_list


@pytest.fixture
def initial_game_state_with_three_users() -> GameState:
    return GameState.get_initial_game_state(users=["user_1", "user_2", "user_3"])


@pytest.fixture
def initial_game_state_with_four_users() -> GameState:
    return GameState.get_initial_game_state(users=["user_1", "user_2", "user_3", "user_4"])


def _gets_card_for_exchange(decks: dict[USER, list[Card]]) -> list[list[Card]]:
    return [cards[:3] for cards in decks.values()]


def test_validate_payload(initial_game_state_with_four_users: GameState) -> None:
    step = CardExchangeStep(game_state=initial_game_state_with_four_users, local_state=CardExchangeState())
    decks = initial_game_state_with_four_users.decks
    payload = CardExchangePayload(user="user_1", cards=decks["user_1"][:2] + decks["user_2"][:1])
    with pytest.raises(InvalidPayloadBody):
        step.validate_payload(payload=payload)


def test_dispatch_payload_when_not_all_three_players_had_put_cards_for_exchange(
    initial_game_state_with_three_users: GameState,
) -> None:
    step = CardExchangeStep(game_state=initial_game_state_with_three_users, local_state=CardExchangeState())
    cards_for_exchange_1, cards_for_exchange_2, _ = _gets_card_for_exchange(
        decks=initial_game_state_with_three_users.decks
    )
    payload_1 = CardExchangePayload(user="user_1", cards=cards_for_exchange_1)
    payload_2 = CardExchangePayload(user="user_2", cards=cards_for_exchange_2)

    state_1 = step.dispatch_payload(payload=payload_1)
    state_2 = step.dispatch_payload(payload=payload_2)

    assert state_1 == state_2 == initial_game_state_with_three_users
    assert step.local_state.cards_to_exchange == {"user_1": cards_for_exchange_1, "user_2": cards_for_exchange_2}


def test_dispatch_payload_when_not_all_four_players_had_put_cards_for_exchange(
    initial_game_state_with_four_users: GameState,
) -> None:
    step = CardExchangeStep(game_state=initial_game_state_with_four_users, local_state=CardExchangeState())
    cards_for_exchange_1, cards_for_exchange_2, cards_for_exchange_3, _ = _gets_card_for_exchange(
        decks=initial_game_state_with_four_users.decks
    )
    payload_1 = CardExchangePayload(user="user_1", cards=cards_for_exchange_1)
    payload_2 = CardExchangePayload(user="user_2", cards=cards_for_exchange_2)
    payload_3 = CardExchangePayload(user="user_3", cards=cards_for_exchange_3)

    state_1 = step.dispatch_payload(payload=payload_1)
    state_2 = step.dispatch_payload(payload=payload_2)
    state_3 = step.dispatch_payload(payload=payload_3)

    assert state_1 == state_2 == state_3 == initial_game_state_with_four_users
    assert step.local_state.cards_to_exchange == {
        "user_1": cards_for_exchange_1,
        "user_2": cards_for_exchange_2,
        "user_3": cards_for_exchange_3,
    }


def test_get_decks_with_cards_exchanged() -> None:
    initial_state = GameState(
        current_user=None,
        users=["user_1", "user_2", "user_3"],
        scores={"user_1": 0, "user_2": 0, "user_3": 0},
        decks={
            "user_1": [SPADE_2, SPADE_3, SPADE_4],
            "user_2": [HEART_2, HEART_3, HEART_4],
            "user_3": [DIAMOND_2, DIAMOND_3, DIAMOND_4],
        },
    )
    step = CardExchangeStep(
        game_state=initial_state,
        local_state=CardExchangeState(
            cards_to_exchange={"user_1": [SPADE_2, SPADE_3, SPADE_4], "user_2": [HEART_2, HEART_3, HEART_4]}
        ),
    )
    step.dispatch_payload(payload=CardExchangePayload(user="user_3", cards=[DIAMOND_2, DIAMOND_3, DIAMOND_4]))

    # pylint: disable=protected-access
    decks = step._get_decks_with_cards_exchanged()
    assert decks == {
        "user_1": [DIAMOND_2, DIAMOND_3, DIAMOND_4],
        "user_2": [SPADE_2, SPADE_3, SPADE_4],
        "user_3": [HEART_2, HEART_3, HEART_4],
    }


def test_dispatch_payload_when_all_three_players_had_put_cards_for_exchange(
    initial_game_state_with_three_users: GameState,
) -> None:
    step = CardExchangeStep(game_state=initial_game_state_with_three_users, local_state=CardExchangeState())
    cards_for_exchange_1, cards_for_exchange_2, cards_for_exchange_3 = _gets_card_for_exchange(
        decks=initial_game_state_with_three_users.decks
    )

    payload_1 = CardExchangePayload(user="user_1", cards=cards_for_exchange_1)
    payload_2 = CardExchangePayload(user="user_2", cards=cards_for_exchange_2)
    payload_3 = CardExchangePayload(user="user_3", cards=cards_for_exchange_3)

    step.dispatch_payload(payload=payload_1)
    step.dispatch_payload(payload=payload_2)
    new_state = step.dispatch_payload(payload=payload_3)

    assert not step.local_state.cards_to_exchange
    assert new_state != initial_game_state_with_three_users

    assert is_list_contained_by_list(sublist=cards_for_exchange_1, list_container=new_state.decks["user_2"])
    assert is_list_contained_by_list(sublist=cards_for_exchange_2, list_container=new_state.decks["user_3"])
    assert is_list_contained_by_list(sublist=cards_for_exchange_3, list_container=new_state.decks["user_1"])


def test_dispatch_payload_when_all_four_players_had_put_cards_for_exchange(
    initial_game_state_with_four_users: GameState,
) -> None:
    step = CardExchangeStep(game_state=initial_game_state_with_four_users, local_state=CardExchangeState())
    cards_for_exchange_1, cards_for_exchange_2, cards_for_exchange_3, cards_for_exchange_4 = _gets_card_for_exchange(
        decks=initial_game_state_with_four_users.decks
    )

    payload_1 = CardExchangePayload(user="user_1", cards=cards_for_exchange_1)
    payload_2 = CardExchangePayload(user="user_2", cards=cards_for_exchange_2)
    payload_3 = CardExchangePayload(user="user_3", cards=cards_for_exchange_3)
    payload_4 = CardExchangePayload(user="user_4", cards=cards_for_exchange_4)

    step.dispatch_payload(payload=payload_1)
    step.dispatch_payload(payload=payload_2)
    step.dispatch_payload(payload=payload_3)
    new_state = step.dispatch_payload(payload=payload_4)

    assert not step.local_state.cards_to_exchange
    assert new_state != initial_game_state_with_four_users

    assert is_list_contained_by_list(sublist=cards_for_exchange_1, list_container=new_state.decks["user_2"])
    assert is_list_contained_by_list(sublist=cards_for_exchange_2, list_container=new_state.decks["user_3"])
    assert is_list_contained_by_list(sublist=cards_for_exchange_3, list_container=new_state.decks["user_4"])
    assert is_list_contained_by_list(sublist=cards_for_exchange_4, list_container=new_state.decks["user_1"])


def test_should_switch_to_next_step(initial_game_state_with_three_users: GameState) -> None:
    step = CardExchangeStep(game_state=initial_game_state_with_three_users, local_state=CardExchangeState())
    cards_for_exchange_1, cards_for_exchange_2, cards_for_exchange_3 = _gets_card_for_exchange(
        decks=initial_game_state_with_three_users.decks
    )

    payload_1 = CardExchangePayload(user="user_1", cards=cards_for_exchange_1)
    payload_2 = CardExchangePayload(user="user_2", cards=cards_for_exchange_2)
    payload_3 = CardExchangePayload(user="user_3", cards=cards_for_exchange_3)

    step.dispatch_payload(payload=payload_1)
    step.dispatch_payload(payload=payload_2)
    step.dispatch_payload(payload=payload_3)

    assert step.should_switch_to_next_step
