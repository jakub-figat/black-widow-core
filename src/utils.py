import datetime as dt
import json
from typing import Any
from uuid import UUID

from pydantic import ValidationError

from src.enums.websocket import PayloadType


def is_list_contained_by_list(sublist: list[Any], list_container: list[Any]) -> bool:
    for elem in sublist:
        if elem not in list_container:
            return False

    return True


class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (dt.date, dt.datetime)):
            return obj.isoformat()

        if isinstance(obj, UUID):
            return str(obj)

        return super().default(obj)


class DateTimeJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, source: dict[str, Any]) -> dict[str, Any]:
        for key, value in source.items():
            if isinstance(value, str):
                try:
                    source[key] = dt.datetime.fromisoformat(value)
                except:  # NOQA
                    pass
        return source


def get_response_from_pydantic_error(error: ValidationError) -> dict[str, Any]:
    return {"detail": error.errors(), "type": PayloadType.VALIDATION_ERROR.value}
