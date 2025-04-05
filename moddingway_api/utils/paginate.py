from typing import Any, Callable, Sequence, Tuple, TypeVar

from fastapi_pagination.api import create_page
from fastapi_pagination.utils import verify_params


def parse_pagination_params() -> Tuple[int, int]:
    params, _ = verify_params(None, "limit-offset")

    return (params.page, params.size)


T = TypeVar("T")


def paginate(
    sequence: Sequence[T], length_function: Callable[[Sequence[T]], int]
) -> Any:
    params, _ = verify_params(None, "limit-offset")

    total = length_function(sequence)

    # create page object with paginated items
    return create_page(
        sequence,
        params=params,
        total=total,
    )
