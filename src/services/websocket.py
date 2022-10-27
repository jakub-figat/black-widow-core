import json
from typing import Any, Optional

from mypy_boto3_apigateway.client import APIGatewayClient

from src.data_access.game import GameDataAccess
from src.data_access.lobby import LobbyDataAccess
from src.data_access.user import UserDataAccess
from src.enums.websocket import PayloadType
from src.schemas.game import GameModel
from src.schemas.lobby import LobbyModel
from src.schemas.user import UserModel
from src.schemas.websocket import (
    CreateLobbyPayload,
    GameDetailSchema,
    GamePreviewSchema,
    GetGameDetailPayload,
    JoinLobbyPayload,
    LeaveLobbyPayload,
    MakeMovePayload,
)
from src.services.game import GameService
from src.utils import DateTimeJSONEncoder


class WebsocketHandler:
    def __init__(
        self,
        user_data_access: UserDataAccess,
        lobby_data_access: LobbyDataAccess,
        game_data_access: GameDataAccess,
        game_service: GameService,
        api_gateway_client: APIGatewayClient,
    ) -> None:
        self.user_data_access = user_data_access
        self.lobby_data_access = lobby_data_access
        self.game_data_access = game_data_access
        self.game_service = game_service
        self.api_gateway_client = api_gateway_client

    def send_to_connection(self, *, body: dict[str, Any], connection_id: str) -> None:
        self.api_gateway_client.post_to_connection(
            Data=json.dumps(body, cls=DateTimeJSONEncoder).encode("utf-8"), ConnectionId=connection_id
        )

    def send_to_users(
        self,
        *,
        body: dict[str, Any],
        users: list[UserModel],
        excluded_connection: Optional[str] = None,
    ) -> None:
        for user in users:
            for user_connection_id in user.connection_ids:
                if user_connection_id == excluded_connection:
                    continue

                self.api_gateway_client.post_to_connection(
                    Data=json.dumps(body, cls=DateTimeJSONEncoder).encode("utf-8"),
                    ConnectionId=user_connection_id,
                )

    def connect_user(self, *, user_id: str, connection_id: str) -> None:
        user = self.user_data_access.get(pk="user", sk=f"user#{user_id}")
        if user is None:
            user = UserModel(email=user_id)

        user.connection_ids.append(connection_id)
        self.user_data_access.save(model=user)

    def disconnect_user(self, *, user_id: str, connection_id: str) -> None:
        user = self.user_data_access.get(pk="user", sk=f"user#{user_id}")
        user.connection_ids.remove(connection_id)
        self.user_data_access.save(model=user)

    def send_lobbies_list_to_connection(self, *, lobbies: list[LobbyModel], connection_id: str) -> None:
        self.send_to_connection(
            body={
                "type": PayloadType.LOBBIES_LIST.value,
                "lobbies": [lobby.dict(by_alias=True) for lobby in lobbies],
            },
            connection_id=connection_id,
        )

    def send_lobby_updated_to_users(self, *, users: list[UserModel], lobby: LobbyModel) -> None:
        for user in users:
            for connection_id in user.connection_ids:
                self.send_to_connection(
                    body={"type": PayloadType.LOBBY_UPDATED.value, "lobby": lobby.dict(by_alias=True)},
                    connection_id=connection_id,
                )

    def send_lobby_deleted_to_users(self, *, users: list[UserModel], lobby_id: str) -> None:
        for user in users:
            for connection_id in user.connection_ids:
                self.send_to_connection(
                    body={"type": PayloadType.LOBBY_DELETED.value, "lobbyId": lobby_id}, connection_id=connection_id
                )

    def send_games_preview_to_connection(self, *, games: list[GameModel], connection_id: str) -> None:
        self.send_to_connection(
            body={
                "type": PayloadType.GAMES_LIST.value,
                "games": [GamePreviewSchema.from_game(game=game).dict(by_alias=True) for game in games],
            },
            connection_id=connection_id,
        )

    def send_game_preview_updated_to_users(self, *, users: list[UserModel], game: GameModel) -> None:
        for user in users:
            for connection_id in user.connection_ids:
                self.send_to_connection(
                    body={"type": PayloadType.GAME_UPDATED, "game": GamePreviewSchema.from_game(game=game)},
                    connection_id=connection_id,
                )

    def send_game_preview_deleted_to_users(self, *, users: list[UserModel], game_id: str) -> None:
        for user in users:
            for connection_id in user.connection_ids:
                self.send_to_connection(
                    body={"type": PayloadType.GAME_UPDATED, "gameId": game_id}, connection_id=connection_id
                )

    def send_game_detail_to_connection(self, *, game: GameModel, user_id: str, connection_id: str) -> None:
        self.send_to_connection(
            body={
                "type": PayloadType.GAME_DETAIL,
                "game": GameDetailSchema.from_game(game=game, user_id=user_id).dict(by_alias=True),
            },
            connection_id=connection_id,
        )

    def send_game_detail_updated_to_users(self, *, game: GameModel) -> None:
        for user_id in game.game.state.users:
            user = self.user_data_access.get(pk="user", sk=f"user#{user_id}")
            for connection_id in user.connection_ids:
                self.send_to_connection(
                    body={
                        "type": PayloadType.GAME_DETAIL_UPDATED.value,
                        "game": GameDetailSchema.from_game(game=game, user_id=user_id).dict(by_alias=True),
                    },
                    connection_id=connection_id,
                )

    def send_game_detail_deleted_to_users(self, *, game: GameModel) -> None:
        for user_id in game.game.state.users:
            user = self.user_data_access.get(pk="user", sk=f"user#{user_id}")
            for connection_id in user.connection_ids:
                self.send_to_connection(
                    body={
                        "type": PayloadType.GAME_DETAIL_DELETED.value,
                        "gameId": game.game_id,
                    },
                    connection_id=connection_id,
                )

    def create_lobby(self, *, payload: CreateLobbyPayload, user_id: str) -> LobbyModel:
        user = self.user_data_access.get(pk="user", sk=f"user#{user_id}")
        return self.game_service.create_lobby(user=user, max_players=payload.max_players)

    def join_lobby(self, *, payload: JoinLobbyPayload, user_id: str) -> Optional[GameModel]:
        user = self.user_data_access.get(pk="user", sk=f"user#{user_id}")
        return self.game_service.add_user_to_lobby(lobby_id=payload.lobby_id, user=user)

    def leave_lobby(self, *, payload: LeaveLobbyPayload, user_id: str) -> bool:
        user = self.user_data_access.get(pk="user", sk=f"user#{user_id}")
        return self.game_service.remove_user_from_lobby(lobby_id=payload.lobby_id, user=user)

    def get_game_detail(self, *, payload: GetGameDetailPayload, user_id: str) -> GameModel:
        return self.game_service.get_game_with_user(game_id=payload.game_id, user_id=user_id)

    def make_move(self, *, payload: MakeMovePayload, user_id: str) -> GameModel:
        user = self.user_data_access.get(pk="user", sk=f"user#{user_id}")
        return self.game_service.dispatch_game_action(game_id=payload.game_id, payload=payload.game_payload, user=user)
