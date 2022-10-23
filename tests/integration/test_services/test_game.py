from uuid import uuid4

import pytest
from mypy_boto3_dynamodb.service_resource import Table
from pydantic import ValidationError

from src.core.game import Game
from src.data_access.exceptions import DataAccessException, DoesNotExist
from src.data_access.game import GameDataAccess
from src.data_access.lobby import LobbyDataAccess
from src.data_access.user import UserDataAccess
from src.schemas.game import GameModel
from src.schemas.user import UserModel
from src.services.game import GameService


@pytest.fixture
def game_service(dynamodb_testcase_table: Table) -> GameService:
    table_name = dynamodb_testcase_table.table_name
    return GameService(
        game_data_access=GameDataAccess(table_name=table_name),
        lobby_data_access=LobbyDataAccess(table_name=table_name),
        user_data_access=UserDataAccess(table_name=table_name),
    )


def test_game_service_create_lobby_and_add_player(game_service: GameService) -> None:
    user = UserModel(email="test@test.com")
    other_user = UserModel(email="other@test.com")
    game_service._user_data_access.save(model=user)

    lobby = game_service.create_lobby(user=user)
    game_service.add_user_to_lobby(lobby_id=lobby.lobby_id, user=other_user)

    lobby = game_service._lobby_data_access.get(**lobby.key)
    user = game_service._user_data_access.get(**user.key)
    other_user = game_service._user_data_access.get(**other_user.key)

    assert len(lobby.users) == 2
    assert lobby.lobby_id in user.lobbies_ids
    assert lobby.lobby_id in other_user.lobbies_ids


def test_game_service_add_user_to_not_existing_lobby(game_service: GameService) -> None:
    with pytest.raises(DoesNotExist, match="Lobby with id *"):
        game_service.add_user_to_lobby(lobby_id="xdddd", user=UserModel(email="test@test.pl"))


def test_game_service_create_lobby_game_started_with_all_players(game_service: GameService) -> None:
    users = [UserModel(email=f"test{str(num)}") for num in range(1, 4)]
    game_service._user_data_access.bulk_save(models=users)

    lobby = game_service.create_lobby(user=users[0])
    game_service.add_user_to_lobby(lobby_id=lobby.lobby_id, user=users[1])
    game = game_service.add_user_to_lobby(lobby_id=lobby.lobby_id, user=users[2])

    assert game is not None
    assert game_service._lobby_data_access.get(**lobby.key) is None

    users = [game_service._user_data_access.get(**user.key) for user in users]
    for user in users:
        assert user.lobbies_ids == []
        assert len(user.games_ids) == 1


def test_game_service_remove_user_from_lobby(game_service: GameService) -> None:
    user = UserModel(email="someuserr@test.com")
    game_service._user_data_access.save(model=user)
    lobby = game_service.create_lobby(user=user)
    game_service.remove_user_from_lobby(lobby_id=lobby.lobby_id, user=user)

    lobby = game_service._lobby_data_access.get(pk=lobby.pk, sk=lobby.sk)
    user = game_service._user_data_access.get(pk=user.pk, sk=user.sk)

    assert lobby.users == []
    assert user.lobbies_ids == []


def test_game_service_remove_user_lobby_without_correct_user(game_service: GameService) -> None:
    user = UserModel(email="someuserr@test.com")
    game_service._user_data_access.save(model=user)
    lobby = game_service.create_lobby(user=user)
    with pytest.raises(DataAccessException, match=f"User doesnotexist@test.com not found in lobby {lobby.lobby_id}"):
        game_service.remove_user_from_lobby(lobby_id=lobby.lobby_id, user=UserModel(email="doesnotexist@test.com"))


def test_game_service_remove_user_from_not_existing_lobby(game_service: GameService) -> None:
    with pytest.raises(DoesNotExist, match="Lobby with id *"):
        game_service.remove_user_from_lobby(lobby_id="xdddd", user=UserModel(email="test@test.pl"))


def test_game_service_dispatch_game_action_after_game_begins(game_service: GameService) -> None:
    user = UserModel(email="user1@test.com")
    game_model = GameModel(
        game_id=str(uuid4()), game=Game.start_game(users=["user1@test.com", "user2@test.com", "user3@test.com"])
    )
    game_before = game_model.game
    game_service._game_data_access.save(model=game_model)
    user_cards = game_model.game.state.decks[user.email][:3]
    game_service.dispatch_game_action(user=user, game_id=game_model.game_id, payload={"cards": user_cards})

    game_model = game_service._game_data_access.get(**game_model.key)

    assert game_model.game.current_step.__class__ == game_before.current_step.__class__
    assert game_model.game.current_step != game_before.current_step


def test_game_service_dispatch_game_action_raises_validation_error_with_invalid_payload(
    game_service: GameService,
) -> None:
    user = UserModel(email="user1@test.com")
    game = GameModel(
        game_id=str(uuid4()), game=Game.start_game(users=["user1@test.com", "user2@test.com", "user3@test.com"])
    )
    game_service._game_data_access.save(model=game)
    with pytest.raises(ValidationError):
        game_service.dispatch_game_action(game_id=game.game_id, user=user, payload={})
