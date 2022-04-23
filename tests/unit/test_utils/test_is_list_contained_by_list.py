from typing import Any

import pytest

from src.utils import is_list_contained_by_list


@pytest.mark.parametrize(
    "list_1,list_2,result",
    [
        (["1"], ["1"], True),
        (["1"], ["2"], False),
        (["1"], ["3", "1", "2"], True),
        ([1], [3, 1, 2], True),
        ([1], ["3", "1", "2"], False),
        ([1], ["3", "1", "2", 1], True),
    ],
)
def test_is_list_contained_by_list(list_1: list[Any], list_2: list[Any], result: bool) -> None:
    assert is_list_contained_by_list(sublist=list_1, list_container=list_2) is result
