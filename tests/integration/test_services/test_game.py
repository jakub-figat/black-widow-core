import pytest
from mypy_boto3_dynamodb.service_resource import Table

from src.data_access.game import GameDataAccess
from src.data_access.lobby import LobbyDataAccess
from src.data_access.user import UserDataAccess
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

    lobby = game_service._lobby_data_access.get(pk=f"games#lobby#{lobby.lobby_id}", sk=f"games#lobby#{lobby.lobby_id}")
    user = game_service._user_data_access.get(pk=user.pk, sk=user.sk)
    other_user = game_service._user_data_access.get(pk=other_user.pk, sk=other_user.sk)

    assert len(lobby.users) == 2
    assert lobby.lobby_id in user.lobbies_ids
    assert lobby.lobby_id in other_user.lobbies_ids
