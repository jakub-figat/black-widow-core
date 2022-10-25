import json
from typing import Any, Optional

from mypy_boto3_apigateway.client import APIGatewayClient
from pydantic import ValidationError

from src.data_access.lobby import LobbyDataAccess
from src.data_access.user import UserDataAccess
from src.enums.websocket import PayloadType
from src.schemas.lobby import LobbyModel
from src.schemas.user import UserModel
from src.schemas.websocket import CreateLobbyPayload
from src.services.game import GameService
from src.utils import DateTimeUUIDJSONEncoder, get_response_from_pydantic_error


class WebsocketHandler:
    def __init__(
        self,
        user_data_access: UserDataAccess,
        lobby_data_access: LobbyDataAccess,
        game_service: GameService,
        api_gateway_client: APIGatewayClient,
    ) -> None:
        self.user_data_access = user_data_access
        self.lobby_data_access = lobby_data_access
        self.game_service = game_service
        self.api_gateway_client = api_gateway_client

    def send_to_connection(self, *, body: dict[str, Any], connection_id: str) -> None:
        self.api_gateway_client.post_to_connection(
            Data=json.dumps(body, cls=DateTimeUUIDJSONEncoder).encode("utf-8"), ConnectionId=connection_id
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
                    Data=json.dumps(body, cls=DateTimeUUIDJSONEncoder).encode("utf-8"),
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

    def send_lobbies_to_connection(self, *, lobbies: list[LobbyModel], connection_id: str) -> None:
        self.send_to_connection(
            body={
                "type": PayloadType.LOBBIES_LIST.value,
                "lobbies": [lobby.dict() for lobby in lobbies],
            },
            connection_id=connection_id,
        )

    def send_lobbies_to_users(self, *, users: list[UserModel], lobbies: list[LobbyModel]) -> None:
        for user in users:
            for connection_id in user.connection_ids:
                self.send_lobbies_to_connection(connection_id=connection_id, lobbies=lobbies)

    def create_lobby(self, *, payload: CreateLobbyPayload, user_id: str) -> None:
        user = self.user_data_access.get(pk="user", sk=f"user#{user_id}")
        self.game_service.create_lobby(user=user, max_players=payload.max_players)
        users = self.user_data_access.get_many(pk="user")
        lobbies = self.lobby_data_access.get_many(pk="lobby")
        self.send_lobbies_to_users(users=users, lobbies=lobbies)

    def leave_lobby(self, *, payload: dict[str, Any], user_id: str) -> None:
        user = self.user_data_access.get(pk="user", sk=f"user#{user_id}")

    def handle_user_join_game(self) -> None:
        pass

    def handle_user_send_game_payload(self) -> None:
        pass

    def handle_user_leave_game(self) -> None:
        pass
