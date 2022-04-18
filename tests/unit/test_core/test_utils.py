import itertools

import pytest

from src.core import cards
from src.core.consts import USER
from src.core.utils import get_initial_decks, get_initial_scores


@pytest.mark.parametrize(
    "users,expected_scores",
    [
        (["1", "2", "3"], {"1": 0, "2": 0, "3": 0}),
        (["1", "2", "3", "4"], {"1": 0, "2": 0, "3": 0, "4": 0}),
    ],
)
def test_get_initial_scores(users: list[USER], expected_scores: dict[USER, int]) -> None:
    assert get_initial_scores(users=users) == expected_scores


@pytest.mark.parametrize("users", (["1", "2"], ["1"], [], ["1", "2", "3", "4", "5"]))
def test_get_initial_scores_raises_error_with_invalid_number_of_users(users: list[USER]) -> None:
    with pytest.raises(ValueError):
        get_initial_scores(users=users)


def test_get_initial_decks_with_three_players() -> None:
    users = ["User_1", "User_2", "User_3"]
    decks = get_initial_decks(users=users)
    user_1_cards, user_2_cards, user_3_cards = decks.values()
    all_cards = list(itertools.chain.from_iterable(decks.values()))

    assert len(decks) == 3
    assert len(set(decks)) == len(decks)
    assert cards.CLUB_2 not in all_cards
    assert all_cards.count(cards.CLUB_3) == 1
    assert len(user_1_cards) == len(user_2_cards) == len(user_3_cards) == 17


def test_get_initial_decks_with_four_players() -> None:
    users = ["User_1", "User_2", "User_3", "User_4"]
    decks = get_initial_decks(users=users)
    user_1_cards, user_2_cards, user_3_cards, user_4_cards = decks.values()
    all_cards = list(itertools.chain.from_iterable(decks.values()))

    assert len(decks) == 4
    assert len(set(decks)) == len(decks)
    assert all_cards.count(cards.CLUB_2) == 1
    assert len(user_1_cards) == len(user_2_cards) == len(user_3_cards) == len(user_4_cards) == 13


@pytest.mark.parametrize("users", ([], ["1", "2"], ["1", "2", "3", "4", "5"], ["1", "2", "3", "4", "5", "6"]))
def test_get_initial_decks_with_invalid_number_of_players(users: list[USER]) -> None:
    with pytest.raises(ValueError):
        get_initial_decks(users=users)
