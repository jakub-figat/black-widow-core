from typing import Any


def is_list_contained_by_list(sublist: list[Any], list_container: list[Any]) -> bool:
    for elem in sublist:
        if elem not in list_container:
            return False

    return True
