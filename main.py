import json
from typing import Any

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from mypy_boto3_apigateway.client import APIGatewayClient
from pydantic import ValidationError

from src.data_access.exceptions import DataAccessException
from src.data_access.game import GameDataAccess
from src.data_access.lobby import LobbyDataAccess
from src.data_access.user import UserDataAccess
from src.enums.websocket import Action, PayloadType, RouteKey
from src.schemas.websocket import CreateLobbyPayload, JoinLobbyPayload, LeaveLobbyPayload
from src.services.exceptions import ServiceException
from src.services.game import GameService
from src.services.websocket import WebsocketHandler
from src.settings import settings
from src.utils import DateTimeJSONDecoder, get_response_from_pydantic_error


logger = Logger()


@logger.inject_lambda_context(log_event=True)
def main_handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    request_context = event.get("requestContext", {})
    user_id = request_context["authorizer"]["principalId"]
    domain = request_context.get("domainName")
    stage = request_context.get("stage")
    connection_id = request_context.get("connectionId")
    route_key = request_context.get("routeKey")

    api_gateway_client: APIGatewayClient = boto3.client(
        "apigatewaymanagementapi", endpoint_url=f"https://{domain}/{stage}"
    )
    table_name = settings.dynamodb_games_table_name
    user_data_access = UserDataAccess(table_name=table_name)
    lobby_data_access = LobbyDataAccess(table_name=table_name)
    game_data_access = GameDataAccess(table_name=table_name)

    websocket_handler = WebsocketHandler(
        user_data_access=user_data_access,
        lobby_data_access=lobby_data_access,
        game_service=GameService(
            game_data_access=game_data_access, lobby_data_access=lobby_data_access, user_data_access=user_data_access
        ),
        api_gateway_client=api_gateway_client,
    )

    if route_key == RouteKey.CONNECT.value:
        websocket_handler.connect_user(user_id=user_id, connection_id=connection_id)
        return {"statusCode": 200}

    if route_key == RouteKey.DISCONNECT.value:
        websocket_handler.disconnect_user(user_id=user_id, connection_id=connection_id)
        return {"statusCode": 200}

    try:
        body = json.loads(event.get("body"), cls=DateTimeJSONDecoder)
    except (json.JSONDecodeError, TypeError):
        websocket_handler.send_to_connection(
            body={"detail": "Invalid JSON body"},
            connection_id=connection_id,
        )
        return {"statusCode": 400}

    payload = body.get("payload", {})
    action = body.get("action")

    try:
        if action == Action.LIST_LOBBIES.value:
            lobbies = lobby_data_access.get_many(pk="lobby")
            websocket_handler.send_lobbies_to_connection(lobbies=lobbies, connection_id=connection_id)

        elif action == Action.CREATE_LOBBY.value:
            payload = CreateLobbyPayload(**payload)
            websocket_handler.create_lobby(payload=payload, user_id=user_id)

            lobbies = websocket_handler.lobby_data_access.get_many(pk="lobby")
            users = websocket_handler.user_data_access.get_many(pk="user")
            websocket_handler.send_lobbies_to_users(users=users, lobbies=lobbies)

        elif action == Action.JOIN_LOBBY.value:
            payload = JoinLobbyPayload(**payload)
            websocket_handler.join_lobby(payload=payload, user_id=user_id)

            lobbies = websocket_handler.lobby_data_access.get_many(pk="lobby")
            users = websocket_handler.user_data_access.get_many(pk="user")
            websocket_handler.send_lobbies_to_users(users=users, lobbies=lobbies)

        elif action == Action.LEAVE_LOBBY.value:
            payload = LeaveLobbyPayload(**payload)
            websocket_handler.leave_lobby(payload=payload, user_id=user_id)
            websocket_handler.send_to_connection(
                body={"type": PayloadType.INFO.value, "detail": f"You've left lobby {payload.lobby_id}"},
                connection_id=connection_id,
            )

            lobbies = websocket_handler.lobby_data_access.get_many(pk="lobby")
            users = websocket_handler.user_data_access.get_many(pk="user")
            websocket_handler.send_lobbies_to_users(users=users, lobbies=lobbies)

        else:
            websocket_handler.send_to_connection(
                body={"type": PayloadType.INVALID_PAYLOAD.value, "detail": f"No action named {action}"},
                connection_id=connection_id,
            )

    except ValidationError as exc:
        websocket_handler.send_to_connection(body=get_response_from_pydantic_error(exc), connection_id=connection_id)
        return {"statusCode": 400}

    except (DataAccessException, ServiceException) as exc:
        websocket_handler.send_to_connection(
            body={"type": PayloadType.ERROR.value, "detail": str(exc)}, connection_id=connection_id
        )

    return {"statusCode": 200}