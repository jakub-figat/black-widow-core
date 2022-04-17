from typing import Any

from src.core.abstract import GameStep


class ExchangeStep(GameStep):
    @classmethod
    def run(cls, *args, **kwargs) -> Any:
        pass
