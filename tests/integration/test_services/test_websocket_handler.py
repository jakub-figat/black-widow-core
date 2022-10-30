import json
from collections import defaultdict
from uuid import uuid4

import pytest
from mypy_boto3_dynamodb.service_resource import Table

from src.core import cards
from src.core.enums import CardSuit
from src.core.exceptions import GameError
from src.core.game import Game, GameSettings
from src.core.state import GameState
from src.core.steps import CardExchangeStep, FinishedStep, FirstRoundStep, InProgressStep
from src.core.types import RoundState
from src.data_access.game import GameDataAccess
from src.data_access.lobby import LobbyDataAccess
from src.data_access.user import UserDataAccess
from src.schemas.game import GameModel
from src.schemas.lobby import LobbyModel
from src.schemas.user import UserModel
from src.schemas.websocket import CreateLobbyPayload, JoinLobbyPayload, LeaveLobbyPayload, MakeMovePayload
from src.services.exceptions import GameServiceException
from src.services.game import GameService
from src.services.websocket import WebsocketHandler
from src.utils import DateTimeJSONDecoder


class FakeAPIGatewayClient:
    def __init__(self) -> None:
        self.messages_sent = defaultdict(list)

    def post_to_connection(self, Data: bytes, ConnectionId: str) -> None:
        self.messages_sent[ConnectionId].append(json.loads(Data.decode("utf-8"), cls=DateTimeJSONDecoder))


@pytest.fixture
def websocket_handler(dynamodb_testcase_table: Table) -> WebsocketHandler:
    user_data_access = UserDataAccess(table_name=dynamodb_testcase_table.table_name)
    lobby_data_access = LobbyDataAccess(table_name=dynamodb_testcase_table.table_name)
    game_data_access = GameDataAccess(table_name=dynamodb_testcase_table.table_name)
    game_service = GameService(game_data_access, user_data_access, lobby_data_access)

    return WebsocketHandler(
        user_data_access=user_data_access,
        lobby_data_access=lobby_data_access,
        game_data_access=game_data_access,
        game_service=game_service,
        api_gateway_client=FakeAPIGatewayClient(),
    )


@pytest.fixture
def user(websocket_handler: WebsocketHandler) -> UserModel:
    user = UserModel(email="test@test.com")
    websocket_handler.user_data_access.save(model=user)
    return user


@pytest.fixture
def user_2(websocket_handler: WebsocketHandler) -> UserModel:
    user = UserModel(email="test2@test.com")
    websocket_handler.user_data_access.save(model=user)
    return user


@pytest.fixture
def user_3(websocket_handler: WebsocketHandler) -> UserModel:
    user = UserModel(email="test3@test.com")
    websocket_handler.user_data_access.save(model=user)
    return user


@pytest.fixture
def game_with_first_round() -> Game:
    settings = GameSettings()
    users = ["test@test.com", "test2@test.com", "test3@test.com"]
    state = GameState(
        users=users,
        decks={
            "test@test.com": [cards.CLUB_KING],
            "tes2@test.com": [cards.SPADE_4],
            "test3@test.com": [cards.CLUB_JACK],
        },
        current_user="test3@test.com",
        scores={"test@test.com": 0, "test2@test.com": 0, "test3@test.com": 0},
    )
    step = FirstRoundStep(
        game_state=state,
        local_state=RoundState(
            cards_on_table={"test@test.com": cards.CLUB_2, "test2@test.com": cards.SPADE_QUEEN},
            table_suit=CardSuit.CLUB,
        ),
    )
    return Game(settings=settings, state=state, current_step=step)


@pytest.fixture
def game_with_last_round() -> Game:
    settings = GameSettings()
    users = ["test@test.com", "test2@test.com", "test3@test.com"]
    state = GameState(
        users=users,
        decks={
            "test@test.com": [],
            "test2@test.com": [],
            "test3@test.com": [cards.HEART_4],
        },
        current_user="test3@test.com",
        scores={"test@test.com": 0, "test2@test.com": 0, "test3@test.com": 97},
    )
    step = InProgressStep(
        game_state=state,
        local_state=RoundState(
            cards_on_table={"test@test.com": cards.HEART_2, "test2@test.com": cards.HEART_3}, table_suit=CardSuit.HEART
        ),
    )
    return Game(settings=settings, state=state, current_step=step)


@pytest.fixture
def game_with_finished_step() -> Game:
    settings = GameSettings()
    users = ["test@test.com", "test2@test.com", "test3@test.com"]
    state = GameState(
        users=users,
        decks={
            "test@test.com": [],
            "test2@test.com": [],
            "test3@test.com": [],
        },
        current_user=None,
        scores={"test@test.com": 0, "test2@test.com": 0, "test3@test.com": 0},
    )
    step = FinishedStep(
        game_state=state,
    )
    return Game(settings=settings, state=state, current_step=step)


@pytest.fixture
def game_model_first_round(
    websocket_handler: WebsocketHandler,
    game_with_first_round: Game,
    user: UserModel,
    user_2: UserModel,
    user_3: UserModel,
) -> GameModel:
    game_model = GameModel(game_id=str(uuid4()), game=game_with_first_round)
    user.games_ids.append(game_model.game_id)
    user_2.games_ids.append(game_model.game_id)
    user_3.games_ids.append(game_model.game_id)

    websocket_handler.user_data_access.bulk_save(models=[user, user_2, user_3])
    websocket_handler.game_data_access.save(model=game_model)

    return game_model


@pytest.fixture
def game_model_last_round(
    websocket_handler: WebsocketHandler,
    game_with_last_round: Game,
    user: UserModel,
    user_2: UserModel,
    user_3: UserModel,
) -> GameModel:
    game_model = GameModel(game_id=str(uuid4()), game=game_with_last_round)
    user.games_ids.append(game_model.game_id)
    user_2.games_ids.append(game_model.game_id)
    user_3.games_ids.append(game_model.game_id)

    websocket_handler.user_data_access.bulk_save(models=[user, user_2, user_3])
    websocket_handler.game_data_access.save(model=game_model)

    return game_model


@pytest.fixture
def game_model_finished(
    websocket_handler: WebsocketHandler,
    game_with_finished_step: Game,
    user: UserModel,
    user_2: UserModel,
    user_3: UserModel,
) -> GameModel:
    game_model = GameModel(game_id=str(uuid4()), game=game_with_finished_step)
    user.games_ids.append(game_model.game_id)
    user_2.games_ids.append(game_model.game_id)
    user_3.games_ids.append(game_model.game_id)

    websocket_handler.user_data_access.bulk_save(models=[user, user_2, user_3])
    websocket_handler.game_data_access.save(model=game_model)

    return game_model


@pytest.fixture
def lobby_with_user(websocket_handler: WebsocketHandler, user: UserModel) -> LobbyModel:
    return websocket_handler.create_lobby(payload=CreateLobbyPayload(max_players=3), user_id=user.email)


def test_websocket_handler_connect_user(websocket_handler: WebsocketHandler, user: UserModel) -> None:
    websocket_handler.connect_user(user_id=user.email, connection_id="fake")
    user = websocket_handler.user_data_access.get(**user.key)

    assert len(user.connection_ids) == 1


def test_websocket_handler_disconnect_user(websocket_handler: WebsocketHandler, user: UserModel) -> None:
    websocket_handler.connect_user(user_id=user.email, connection_id="fake")
    websocket_handler.disconnect_user(user_id=user.email, connection_id="fake")
    user = websocket_handler.user_data_access.get(**user.key)

    assert len(user.connection_ids) == 0


def test_websocket_handler_send_to_connection(websocket_handler: WebsocketHandler) -> None:
    websocket_handler.send_to_connection(body={"detail": "message"}, connection_id="example")
    assert websocket_handler.api_gateway_client.messages_sent["example"][0] == {"detail": "message"}


def test_websocket_handler_create_lobby(websocket_handler: WebsocketHandler, user: UserModel) -> None:
    lobby = websocket_handler.create_lobby(payload=CreateLobbyPayload(max_players=3), user_id=user.email)
    user = websocket_handler.user_data_access.get(**user.key)

    assert lobby.max_players == 3
    assert lobby.lobby_id in user.lobbies_ids
    assert user.email in lobby.users


def test_websocket_handler_join_lobby(
    websocket_handler: WebsocketHandler, lobby_with_user: LobbyModel, user_2: UserModel
) -> None:
    optional_game = websocket_handler.join_lobby(
        payload=JoinLobbyPayload(lobby_id=lobby_with_user.lobby_id), user_id=user_2.email
    )
    lobby = websocket_handler.lobby_data_access.get(**lobby_with_user.key)
    user_2 = websocket_handler.user_data_access.get(**user_2.key)

    assert optional_game is None
    assert len(lobby.users) == 2
    assert lobby.lobby_id in user_2.lobbies_ids


def test_websocket_handler_join_lobby_and_lobby_gets_full(
    websocket_handler: WebsocketHandler, lobby_with_user: LobbyModel, user_2: UserModel, user_3: UserModel
) -> None:
    websocket_handler.join_lobby(payload=JoinLobbyPayload(lobby_id=lobby_with_user.lobby_id), user_id=user_2.email)
    game = websocket_handler.join_lobby(
        payload=JoinLobbyPayload(lobby_id=lobby_with_user.lobby_id), user_id=user_3.email
    )
    lobby = websocket_handler.lobby_data_access.get(**lobby_with_user.key)

    users = websocket_handler.user_data_access.get_many(pk="user")

    assert lobby is None
    assert set(game.game.state.users) == set(user.email for user in users)
    assert game.game_step == CardExchangeStep.__name__

    for user in users:
        assert len(user.lobbies_ids) == 0
        assert game.game_id in user.games_ids


def test_websocket_handler_leave_lobby(
    websocket_handler: WebsocketHandler, lobby_with_user: LobbyModel, user: UserModel, user_2: UserModel
) -> None:
    websocket_handler.join_lobby(payload=JoinLobbyPayload(lobby_id=lobby_with_user.lobby_id), user_id=user_2.email)
    lobby_deleted = websocket_handler.leave_lobby(
        payload=LeaveLobbyPayload(lobby_id=lobby_with_user.lobby_id), user_id=user_2.email
    )
    lobby = websocket_handler.lobby_data_access.get(**lobby_with_user.key)
    user_2 = websocket_handler.user_data_access.get(**user_2.key)

    assert lobby_deleted is False
    assert lobby.users == [user.email]
    assert len(user_2.lobbies_ids) == 0


def test_websocket_handler_leave_lobby_when_user_is_not_in_lobby(
    websocket_handler: WebsocketHandler, lobby_with_user: LobbyModel, user_2: UserModel
) -> None:
    with pytest.raises(
        GameServiceException, match=f"User {user_2.email} not found in lobby {lobby_with_user.lobby_id}"
    ):
        websocket_handler.leave_lobby(
            payload=LeaveLobbyPayload(lobby_id=lobby_with_user.lobby_id), user_id=user_2.email
        )


def test_websocket_handler_leave_lobby_as_last_user(
    websocket_handler: WebsocketHandler, lobby_with_user: LobbyModel, user: UserModel
) -> None:
    lobby_deleted = websocket_handler.leave_lobby(
        payload=LeaveLobbyPayload(lobby_id=lobby_with_user.lobby_id), user_id=user.email
    )
    user = websocket_handler.user_data_access.get(**user.key)
    lobbies = websocket_handler.lobby_data_access.get_many(pk="lobby")

    assert lobby_deleted is True
    assert len(user.lobbies_ids) == 0
    assert len(lobbies) == 0


def test_websocket_handler_make_move_in_first_round(
    websocket_handler: WebsocketHandler, game_model_first_round: GameModel, user_3: UserModel
) -> None:
    game_model = websocket_handler.make_move(
        payload=MakeMovePayload(game_id=game_model_first_round.game_id, game_payload={"card": str(cards.CLUB_JACK)}),
        user_id=user_3.email,
    )
    assert game_model.game_step == InProgressStep.__name__
    assert game_model.game.state.current_user == user_3.email


def test_websocket_handler_make_move_with_incorrect_user(
    websocket_handler: WebsocketHandler, game_model_first_round: GameModel, user_2: UserModel
) -> None:
    with pytest.raises(GameError, match="User is not permitted to perform action now."):
        websocket_handler.make_move(
            payload=MakeMovePayload(
                game_id=game_model_first_round.game_id, game_payload={"card": str(cards.CLUB_JACK)}
            ),
            user_id=user_2.email,
        )


def test_websocket_handler_make_move_with_game_finished(
    websocket_handler: WebsocketHandler, game_model_finished: GameModel, user: UserModel
) -> None:
    with pytest.raises(GameServiceException, match=f"Game with id {game_model_finished.game_id} is already finished"):
        websocket_handler.make_move(
            payload=MakeMovePayload(game_id=game_model_finished.game_id, game_payload={"card": str(cards.CLUB_JACK)}),
            user_id=user.email,
        )


def test_websocket_handler_make_move_in_last_round(
    websocket_handler: WebsocketHandler, game_model_last_round: GameModel, user_3: UserModel
) -> None:
    game_model = websocket_handler.make_move(
        payload=MakeMovePayload(game_id=game_model_last_round.game_id, game_payload={"card": str(cards.HEART_4)}),
        user_id=user_3.email,
    )

    assert game_model.game.is_finished is True
    assert game_model.game_step == FinishedStep.__name__
    assert game_model.finished_at is not None
