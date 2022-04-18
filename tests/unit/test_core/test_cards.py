import pytest

from src.core import cards
from src.core.exceptions import InvalidCardComparison


@pytest.mark.parametrize(
    "card_1,card_2,is_greater_than",
    [
        (cards.CLUB_2, cards.CLUB_3, False),
        (cards.CLUB_3, cards.CLUB_2, True),
        (cards.DIAMOND_KING, cards.DIAMOND_2, True),
        (cards.HEART_QUEEN, cards.HEART_JACK, True),
        (cards.SPADE_QUEEN, cards.SPADE_ACE, False),
    ],
)
def test_cards_overloaded_gt(card_1: cards.Card, card_2: cards.Card, is_greater_than: bool) -> None:
    assert (card_1 > card_2) is is_greater_than


@pytest.mark.parametrize("card_1,card_2", [(cards.CLUB_2, cards.SPADE_ACE), (cards.HEART_QUEEN, cards.DIAMOND_2)])
def test_cards_overloaded_gt_with_different_suits(card_1: cards.Card, card_2: cards.Card) -> None:
    with pytest.raises(InvalidCardComparison):
        card_1.__gt__(card_2)


@pytest.mark.parametrize(
    "card_1,card_2,is_lower_than",
    [
        (cards.CLUB_2, cards.CLUB_3, True),
        (cards.CLUB_3, cards.CLUB_2, False),
        (cards.DIAMOND_KING, cards.DIAMOND_2, False),
        (cards.HEART_QUEEN, cards.HEART_JACK, False),
        (cards.SPADE_QUEEN, cards.SPADE_ACE, True),
    ],
)
def test_cards_overloaded_lt(card_1: cards.Card, card_2: cards.Card, is_lower_than: bool) -> None:
    assert (card_1 < card_2) is is_lower_than


@pytest.mark.parametrize("card_1,card_2", [(cards.CLUB_2, cards.SPADE_ACE), (cards.HEART_QUEEN, cards.DIAMOND_2)])
def test_cards_overloaded_gt_with_different_suits(card_1: cards.Card, card_2: cards.Card) -> None:
    with pytest.raises(InvalidCardComparison):
        card_1.__lt__(card_2)
