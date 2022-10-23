import json
from typing import Any, Optional

from mypy_boto3_apigateway import APIGatewayClient

from src.data_access import user_data_access
from src.schemas.user import UserModel


def is_list_contained_by_list(sublist: list[Any], list_container: list[Any]) -> bool:
    for elem in sublist:
        if elem not in list_container:
            return False

    return True


def send_message_to_users(
    message: str,
    users: list[UserModel],
    api_gateway_client: APIGatewayClient,
    excluded_connection: Optional[str] = None,
) -> None:
    for user in users:
        for user_connection_id in user.connection_ids:
            if user_connection_id == excluded_connection:
                continue

            api_gateway_client.post_to_connection(
                Data=json.dumps({"message": message}).encode("utf-8"),
                ConnectionId=user_connection_id,
            )
