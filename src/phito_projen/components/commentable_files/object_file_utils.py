from typing import Any, List, Tuple


def get_reference_by_path(path: str, dictlike: dict) -> Any:
    """
    Get a reference to a value in a ``dictlike`` object using a dot-notation string.

    :param path: a string supporting dot-notation and array indices (like the ``jq`` CLI)
    :param dictlike: object with an interface like a dict

    .. code-block:: python

        obj = {
            "friends": [
                {"name": "murphy"},
                {"name": "jobillydoo"},
                {"name": "barrpiddles"},
            ]
        }
        val = get_reference_by_path("friends.[1].name", obj)
        print(val)

    Should return a reference to ``jobillydoo``.
    """

    parts = path.split(".")
    value = get_value(parts[0], dictlike)

    if len(parts) > 1:
        for part in parts[1:]:
            value = get_value(key=part, obj=value)

    return value


def calc_indentation_of_path(path: str, indent: int, list_item_indent: int) -> int:
    parts: List[str] = path.split(".")

    parts_that_are_array_indices = [part for part in parts if is_array_idx(part)]
    parts_that_are_not_array_indices = set(parts) - set(parts_that_are_array_indices)

    total_indentation_from_list_items = (
        len(parts_that_are_array_indices)
    ) * list_item_indent
    total_indentation_from_non_list_items = (
        len(parts_that_are_not_array_indices) - 1
    ) * indent

    return total_indentation_from_list_items + total_indentation_from_non_list_items


def get_reference_container_by_path(path: str, obj: dict) -> Any:
    parts = path.split(".")
    if len(parts) == 1:
        return obj

    parts = path.split(".")
    path_ = ".".join(parts[:-1])
    return get_reference_by_path(path_, obj)


def get_final_key_in_path(path: str):
    last_part: str = path.split(".")[-1]
    return get_scalar_key(last_part)


def is_array_idx(part: str) -> bool:
    return part.startswith("[") and part.endswith("]")


def is_slice(part: str) -> bool:
    return part.count(":") == 1


def get_array_idx(part: str) -> int:
    idx_as_string = part.strip("[").strip("]")
    return int(idx_as_string)


def get_slice_bounds(part: str) -> Tuple[int, int]:
    lower, upper = part.strip("[").strip("]").split(":")
    return int(lower), int(upper)


def get_scalar_key(part: str) -> int | str:
    if is_array_idx(part):
        return get_array_idx(part)
    return part


def get_value(key: str, obj: Any) -> Any:
    if not is_array_idx(key):
        return obj[key]

    if is_slice(key):
        lower, upper = get_slice_bounds(key)
        return obj[lower:upper]

    array_idx: int = get_array_idx(key)
    return obj[array_idx]
