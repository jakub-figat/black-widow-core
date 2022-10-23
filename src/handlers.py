import json
from typing import Any

import boto3
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from mypy_boto3_apigateway.client import APIGatewayClient

from src.data_access import user_data_access
from src.schemas.user import UserModel
from src.utils import send_message_to_users


logger = Logger()


"""
Sending data to users

1. list of users in lobby list
2. list of users in lobby
3. list of users in game
"""


# on connect
def handle_user_connect_to_lobby_list(user_id: str, connection_id: str, api_gateway_client: APIGatewayClient) -> None:
    users = user_data_access.get_many(pk="user")
    send_message_to_users(
        users=users,
        message=f"User {user_id} has joined our server!",
        api_gateway_client=api_gateway_client,
        excluded_connection=connection_id,
    )

    user = user_data_access.get(pk="user", sk=f"user#{user_id}")
    if user is None:
        user = UserModel(email=user_id)

    user.connection_ids.append(connection_id)
    user_data_access.save(model=user)


def handle_user_disconnect_from_lobby_list(
    user_id: str, connection_id: str, api_gateway_client: APIGatewayClient
) -> None:
    users = user_data_access.get_many(pk="user")
    send_message_to_users(
        users=users,
        message=f"User {user_id} has disconnected!",
        api_gateway_client=api_gateway_client,
        excluded_connection=connection_id,
    )

    user = user_data_access.get(pk="user", sk=f"user#{user_id}")
    user.connection_ids.remove(connection_id)
    user_data_access.save(model=user)


def handle_user_sends_message(message: str, user_id: str, api_gateway_client: APIGatewayClient) -> None:
    users = user_data_access.get_many(pk="user")
    send_message_to_users(message=f"{user_id}: {message}", users=users, api_gateway_client=api_gateway_client)


def handle_user_create_lobby(event: dict[str, Any], context: LambdaContext) -> None:
    pass


def handle_user_leave_lobby(event: dict[str, Any], context: LambdaContext) -> None:
    pass


def handle_user_join_game(event: dict[str, Any], context: LambdaContext) -> None:
    pass


def handle_user_send_game_payload(event: dict[str, Any], context: LambdaContext) -> None:
    pass


def handle_user_leave_game(event: dict[str, Any], context: LambdaContext) -> None:
    pass


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

    if route_key == "$connect":
        handle_user_connect_to_lobby_list(
            user_id=user_id,
            connection_id=connection_id,
            api_gateway_client=api_gateway_client,
        )
        return {"statusCode": 200, "body": f"Welcome to our server, {user_id.split('@')[0]}!"}
    elif route_key == "$default":
        handle_user_sends_message(
            message=json.loads(event.get("body", "{}")).get("message", "Default message"),
            user_id=user_id,
            api_gateway_client=api_gateway_client,
        )
        return {"statusCode": 200, "body": "You sent a message, as of now we cannot reply xD"}
    elif route_key == "$disconnect":
        handle_user_disconnect_from_lobby_list(
            user_id=request_context["authorizer"]["principalId"],
            connection_id=connection_id,
            api_gateway_client=api_gateway_client,
        )
        return {"statusCode": 200, "body": f"See you soon, {user_id.split('@')[0]}!"}
