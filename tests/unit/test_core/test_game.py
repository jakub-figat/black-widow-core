import logging
from itertools import chain

import pytest
from _pytest.logging import LogCaptureFixture

from src.core import cards
from src.core.consts import USER
from src.core.enums import CardSuit
from src.core.exceptions import InvalidPayloadBody
from src.core.game import Game, GameSettings
from src.core.state import GameState
from src.core.steps import CardExchangeStep, FinishedStep, FirstRoundStep, InProgressStep
from src.core.types import CardExchangePayload, FinishedPayload, RoundPayload, RoundState


def _get_card_for_exchange(decks: dict[USER, list[cards.Card]]) -> list[list[str]]:
    return [[str(card) for card in cards[:3]] for cards in decks.values()]


@pytest.fixture
def game_with_first_round() -> Game:
    settings = GameSettings()
    users = ["user_1", "user_2", "user_3", "user_4"]
    state = GameState(
        users=users,
        decks={
            "user_1": [cards.CLUB_KING],
            "user_2": [cards.SPADE_4],
            "user_3": [cards.HEART_5],
            "user_4": [cards.CLUB_7],
        },
        current_user="user_4",
        scores={"user_1": 0, "user_2": 0, "user_3": 0, "user_4": 0},
    )
    step = FirstRoundStep(
        game_state=state,
        local_state=RoundState(
            cards_on_table={"user_1": cards.CLUB_2, "user_2": cards.SPADE_QUEEN, "user_3": cards.CLUB_JACK},
            table_suit=CardSuit.CLUB,
        ),
    )
    return Game(settings=settings, state=state, current_step=step)


@pytest.fixture
def game_with_decks_ending() -> Game:
    settings = GameSettings()
    users = ["user_1", "user_2", "user_3", "user_4"]
    state = GameState(
        users=users,
        decks={
            "user_1": [cards.DIAMOND_6, cards.HEART_3],
            "user_2": [cards.DIAMOND_KING, cards.CLUB_KING],
            "user_3": [cards.DIAMOND_QUEEN, cards.DIAMOND_3],
            "user_4": [cards.HEART_5, cards.HEART_KING],
        },
        current_user="user_1",
        scores={"user_1": 0, "user_2": 0, "user_3": 0, "user_4": 0},
    )
    step = FirstRoundStep(
        game_state=state,
    )
    return Game(settings=settings, state=state, current_step=step)


@pytest.fixture
def game_with_finished_step() -> Game:
    settings = GameSettings()
    users = ["user_1", "user_2", "user_3", "user_4"]
    state = GameState(
        users=users,
        decks={
            "user_1": [],
            "user_2": [],
            "user_3": [],
            "user_4": [],
        },
        current_user=None,
        scores={"user_1": 0, "user_2": 0, "user_3": 0, "user_4": 0},
    )
    step = FinishedStep(
        game_state=state,
    )
    return Game(settings=settings, state=state, current_step=step)


@pytest.mark.parametrize("users", (["user_1", "user_2", "user_3"], ["user_1", "user_2", "user_3", "user_4"]))
def test_start_game(users: list[USER]) -> None:
    game = Game.start_game(users=users)

    assert game.state.users == users
    assert len(game.state.decks) == len(users)
    assert isinstance(game.current_step, CardExchangeStep)
    assert game.is_finished is False


def test_exchange_cards() -> None:
    game = Game.start_game(users=["user_1", "user_2", "user_3"])
    cards_for_exchange_1, cards_for_exchange_2, cards_for_exchange_3 = _get_card_for_exchange(decks=game.state.decks)

    payload_1 = CardExchangePayload(user="user_1", cards=[str(card) for card in cards_for_exchange_1])
    payload_2 = CardExchangePayload(user="user_2", cards=[str(card) for card in cards_for_exchange_2])
    payload_3 = CardExchangePayload(user="user_3", cards=[str(card) for card in cards_for_exchange_3])

    game.dispatch(payload=payload_1)
    game.dispatch(payload=payload_2)
    game.dispatch(payload=payload_3)

    assert isinstance(game.current_step, FirstRoundStep)
    assert len(list(chain.from_iterable(game.state.decks.values()))) == 50
    assert game.current_step.local_state.cards_on_table
    assert game.state.current_user is not None
    assert game.is_finished is False


def test_exchange_cards_with_invalid_payload() -> None:
    game = Game.start_game(users=["user_1", "user_2", "user_3"])
    cards_for_exchange_1, _, _ = _get_card_for_exchange(decks=game.state.decks)

    payload = CardExchangePayload(user="user_2", cards=cards_for_exchange_1)

    with pytest.raises(InvalidPayloadBody):
        game.dispatch(payload=payload)


def test_place_card_in_first_round(game_with_first_round: Game) -> None:
    user = game_with_first_round.state.current_user
    card = game_with_first_round.state.decks[user][-1]
    payload = RoundPayload(user=user, card=str(card))

    game_with_first_round.dispatch(payload=payload)

    assert isinstance(game_with_first_round.current_step, InProgressStep)
    assert game_with_first_round.state.scores["user_4"] == 13
    assert game_with_first_round.state.current_user == "user_4"
    assert game_with_first_round.state.decks == {
        "user_1": [cards.CLUB_KING],
        "user_2": [cards.SPADE_4],
        "user_3": [cards.HEART_5],
        "user_4": [],
    }
    assert game_with_first_round.is_finished is False


def test_place_card_in_ending_round(game_with_decks_ending: Game) -> None:
    payload_1 = RoundPayload(user="user_1", card=str(game_with_decks_ending.state.decks["user_1"][0]))
    payload_2 = RoundPayload(user="user_2", card=str(game_with_decks_ending.state.decks["user_2"][0]))
    payload_3 = RoundPayload(user="user_3", card=str(game_with_decks_ending.state.decks["user_3"][0]))
    payload_4 = RoundPayload(user="user_4", card=str(game_with_decks_ending.state.decks["user_4"][0]))
    game_with_decks_ending.dispatch(payload=payload_1)
    game_with_decks_ending.dispatch(payload=payload_2)
    game_with_decks_ending.dispatch(payload=payload_3)
    game_with_decks_ending.dispatch(payload=payload_4)

    payload_2 = RoundPayload(user="user_2", card=str(game_with_decks_ending.state.decks["user_2"][0]))
    payload_3 = RoundPayload(user="user_3", card=str(game_with_decks_ending.state.decks["user_3"][0]))
    payload_4 = RoundPayload(user="user_4", card=str(game_with_decks_ending.state.decks["user_4"][0]))
    payload_1 = RoundPayload(user="user_1", card=str(game_with_decks_ending.state.decks["user_1"][0]))
    game_with_decks_ending.dispatch(payload=payload_2)
    game_with_decks_ending.dispatch(payload=payload_3)
    game_with_decks_ending.dispatch(payload=payload_4)
    game_with_decks_ending.dispatch(payload=payload_1)

    assert isinstance(game_with_decks_ending.current_step, FinishedStep)
    assert game_with_decks_ending.state.scores == {"user_1": 0, "user_2": 3, "user_3": 0, "user_4": 0}
    assert game_with_decks_ending.state.current_user is None
    assert game_with_decks_ending.state.decks == {
        "user_1": [],
        "user_2": [],
        "user_3": [],
        "user_4": [],
    }
    assert game_with_decks_ending.is_finished is False


def test_place_card_in_ending_round_when_max_score_is_reached(
    game_with_decks_ending: Game, caplog: LogCaptureFixture
) -> None:
    game_with_decks_ending.state.scores["user_2"] = 99
    payload_1 = RoundPayload(user="user_1", card=str(game_with_decks_ending.state.decks["user_1"][0]))
    payload_2 = RoundPayload(user="user_2", card=str(game_with_decks_ending.state.decks["user_2"][0]))
    payload_3 = RoundPayload(user="user_3", card=str(game_with_decks_ending.state.decks["user_3"][0]))
    payload_4 = RoundPayload(user="user_4", card=str(game_with_decks_ending.state.decks["user_4"][0]))
    game_with_decks_ending.dispatch(payload=payload_1)
    game_with_decks_ending.dispatch(payload=payload_2)
    game_with_decks_ending.dispatch(payload=payload_3)
    game_with_decks_ending.dispatch(payload=payload_4)

    payload_2 = RoundPayload(user="user_2", card=str(game_with_decks_ending.state.decks["user_2"][0]))
    payload_3 = RoundPayload(user="user_3", card=str(game_with_decks_ending.state.decks["user_3"][0]))
    payload_4 = RoundPayload(user="user_4", card=str(game_with_decks_ending.state.decks["user_4"][0]))
    payload_1 = RoundPayload(user="user_1", card=str(game_with_decks_ending.state.decks["user_1"][0]))
    game_with_decks_ending.dispatch(payload=payload_2)
    game_with_decks_ending.dispatch(payload=payload_3)
    game_with_decks_ending.dispatch(payload=payload_4)
    game_with_decks_ending.dispatch(payload=payload_1)

    assert isinstance(game_with_decks_ending.current_step, FinishedStep)
    assert game_with_decks_ending.state.scores == {"user_1": 0, "user_2": 102, "user_3": 0, "user_4": 0}
    assert game_with_decks_ending.state.current_user is None
    assert game_with_decks_ending.state.decks == {
        "user_1": [],
        "user_2": [],
        "user_3": [],
        "user_4": [],
    }
    assert game_with_decks_ending.is_finished

    with caplog.at_level(logging.INFO):
        game_with_decks_ending.dispatch(payload=FinishedPayload(user="user_1"))

    assert "Game finished." in caplog.text


def test_game_starting_new_round(game_with_finished_step: Game) -> None:
    for user in game_with_finished_step.state.users:
        game_with_finished_step.dispatch(payload=FinishedPayload(user=user))

    assert isinstance(game_with_finished_step.current_step, CardExchangeStep)
    assert len(list(chain.from_iterable(game_with_finished_step.state.decks.values()))) == 52
    assert not game_with_finished_step.current_step.local_state.cards_to_exchange
    assert game_with_finished_step.state.current_user is None
    assert game_with_finished_step.is_finished is False
