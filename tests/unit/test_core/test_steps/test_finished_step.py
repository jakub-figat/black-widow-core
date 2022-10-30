import pytest

from src.core.exceptions import InvalidPayloadBody
from src.core.state import GameState
from src.core.steps import FinishedStep
from src.core.types import FinishedPayload, FinishedState


@pytest.fixture
def game_state_with_round_finished() -> GameState:
    return GameState(
        users=["user_1", "user_2", "user_3", "user_4"],
        scores={"user_1": 100, "user_2": 0, "user_3": 0, "user_4": 0},
        decks={
            "user_1": [],
            "user_2": [],
            "user_3": [],
            "user_4": [],
        },
    )


@pytest.mark.parametrize(
    "payload,state",
    [
        (FinishedPayload(user="user_1"), FinishedState(users_ready={"user_1"})),
        (FinishedPayload(user="user_2"), FinishedState(users_ready={"user_1", "user_2"})),
    ],
)
def test_validate_payload_raises_error_when_user_tries_to_redeclare_his_readiness(
    payload: FinishedPayload, state: FinishedState, game_state_with_round_finished: GameState
) -> None:
    step = FinishedStep(game_state=game_state_with_round_finished, local_state=state)
    with pytest.raises(InvalidPayloadBody):
        step.validate_payload(payload=payload)


def test_finished_step_on_start_method(game_state_with_round_finished: GameState) -> None:
    game_state_with_round_finished.current_user = "user_2"
    step = FinishedStep(game_state=game_state_with_round_finished)
    new_state = step.on_start()

    assert new_state != game_state_with_round_finished
    assert new_state.current_user is None


@pytest.mark.parametrize(
    "payload,state",
    [
        (FinishedPayload(user="user_1"), FinishedState(users_ready={"user_1"})),
        (FinishedPayload(user="user_2"), FinishedState(users_ready={"user_2"})),
    ],
)
def test_finished_step_when_nobody_claimed_readiness(
    payload: FinishedPayload, state: FinishedState, game_state_with_round_finished: GameState
) -> None:
    step = FinishedStep(game_state=game_state_with_round_finished)
    new_state = step.dispatch_payload(payload)

    assert new_state == game_state_with_round_finished
    assert step.local_state == state


@pytest.mark.parametrize(
    "payload,state",
    [
        (FinishedPayload(user="user_2"), FinishedState(users_ready=["user_1", "user_2"])),
        (FinishedPayload(user="user_3"), FinishedState(users_ready=["user_1", "user_3"])),
    ],
)
def test_finished_step_when_someone_claimed_readiness(
    payload: FinishedPayload, state: FinishedState, game_state_with_round_finished: GameState
) -> None:
    step = FinishedStep(game_state=game_state_with_round_finished, local_state=FinishedState(users_ready=["user_1"]))
    new_state = step.dispatch_payload(payload)

    assert new_state == game_state_with_round_finished
    assert step.local_state == state


def test_finished_step_when_everyone_is_ready(game_state_with_round_finished: GameState) -> None:
    step = FinishedStep(
        game_state=game_state_with_round_finished,
        local_state=FinishedState(users_ready=["user_1", "user_2", "user_3"]),
    )
    new_state = step.dispatch_payload(payload=FinishedPayload(user="user_4"))

    assert new_state != game_state_with_round_finished
    assert new_state.users == game_state_with_round_finished.users
    assert new_state.scores == game_state_with_round_finished.scores


def test_should_switch_to_next_step_when_round_is_finished(game_state_with_round_finished: GameState) -> None:
    step = FinishedStep(
        game_state=game_state_with_round_finished,
        local_state=FinishedState(users_ready={"user_1", "user_2", "user_3", "user_4"}),
    )
    assert step.should_switch_to_next_step


def test_should_switch_to_next_step_when_round_is_not_finished(game_state_with_round_finished: GameState) -> None:
    step = FinishedStep(game_state=game_state_with_round_finished)
    assert step.should_switch_to_next_step is False
