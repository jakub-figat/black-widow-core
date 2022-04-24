import random
from collections import defaultdict
from functools import reduce

from src.core import cards
from src.core.cards import Card
from src.core.consts import USER
from src.core.enums import CardSuit
from src.core.exceptions import FirstUserNotFound, InvalidNumberOfUsers


def get_initial_decks(users: list[USER]) -> dict[USER, list[cards.Card]]:
    if len(users) not in (3, 4):
        raise InvalidNumberOfUsers("Invalid number of players, should be 3 or 4.")

    all_cards = cards.ALL_CARDS[:]
    if len(users) == 3:
        all_cards.remove(cards.CLUB_2)

    random.shuffle(all_cards)
    decks = defaultdict(list)
    for index, card in enumerate(all_cards):
        decks[users[index % len(users)]].append(card)

    return decks


def get_initial_scores(users: list[USER]) -> dict[USER, int]:
    if len(users) not in (3, 4):
        raise InvalidNumberOfUsers("Invalid number of players, only 3 or 4 players can play the game.")

    return {user: 0 for user in users}


def get_first_user_card_tuple(decks: dict[USER, list[cards.Card]]) -> tuple[USER, Card]:
    beginning_card = cards.CLUB_2 if len(decks) == 4 else cards.CLUB_3
    for user, user_cards in decks.items():
        if beginning_card in user_cards:
            return user, beginning_card

    raise FirstUserNotFound("No user has Club 2/3 card, cannot determine first player.")


def get_first_user(decks: dict[USER, list[cards.Card]]) -> str:
    beginning_card = cards.CLUB_2 if len(decks) == 4 else cards.CLUB_3
    for user, user_cards in decks.items():
        if beginning_card in user_cards:
            return user

    raise FirstUserNotFound("No user has Club 2/3 card, cannot determine first player.")


def check_if_user_has_suit(suit: CardSuit, deck: list[cards.Card]) -> bool:
    for card in deck:
        if suit == card.suit:
            return True

    return False


def check_if_user_has_only_one_suit(deck: list[cards.Card]) -> bool:
    suits = set()

    for card in deck:
        suits.add(card.suit.value)
        if len(suits > 1):
            return False

    return True


def count_points_for_cards(deck: list[cards.Card]) -> int:
    card_score_mapping = {
        cards.HEART_2: 1,
        cards.HEART_3: 1,
        cards.HEART_4: 1,
        cards.HEART_5: 1,
        cards.HEART_6: 1,
        cards.HEART_7: 1,
        cards.HEART_8: 1,
        cards.HEART_9: 1,
        cards.HEART_10: 1,
        cards.HEART_JACK: 1,
        cards.HEART_QUEEN: 1,
        cards.HEART_KING: 1,
        cards.HEART_ACE: 1,
        cards.SPADE_QUEEN: 13,
        cards.SPADE_KING: 10,
        cards.SPADE_ACE: 7,
    }
    return reduce(lambda total_score, card: total_score + card_score_mapping.get(card, 0), deck, initial=0)
