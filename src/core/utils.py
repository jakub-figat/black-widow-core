import random
from collections import defaultdict

from src.core import cards
from src.core.consts import USER


def get_initial_decks(users: list[USER]) -> dict[USER, list[cards.Card]]:
    all_cards = cards.ALL_CARDS[:]
    random.shuffle(all_cards)
    decks = defaultdict(list)
    for index, card in enumerate(all_cards):
        decks[users[index % len(users)]].append(card)

    return decks


def get_initial_scores(users: list[USER]) -> dict[USER, int]:
    return {user: 0 for user in users}


def get_first_player(decks: dict[USER, list[cards.Card]]) -> str:
    beginning_card = cards.CLUB_2 if len(decks) == 4 else cards.CLUB_3
    for user, user_cards in decks.items():
        if beginning_card in user_cards:
            return user

    raise ValueError("No user has Club 2/3 card, cannot determine first player.")
