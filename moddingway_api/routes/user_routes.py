from typing import Optional

from fastapi import APIRouter
from fastapi_pagination import Page

from moddingway_api.schemas.user_schema import User
from moddingway_api.utils.paginate import paginate, parse_pagination_params

router = APIRouter(prefix="/users")


@router.get("/{user_id}")
async def get_user_by_id(user_id: int) -> Optional[User]:
    # This code is meant to demonstrate a get response
    # feel free to modify it for actual purposes as necessary
    return User(userID=str(user_id), isMod=False, strikePoints=1)


# @router.get("")
# async def get_users(page: int = 1, size: int = 50) -> UserPage:
#     # This code is meant to demonstrate a get response
#     # feel free to modify it for actual purposes as necessary
#     return UserPage(
#         items=[
#             User(userID=str(1), isMod=False, strikePoints=1),
#             User(userID=str(2), isMod=False, strikePoints=0),
#         ],
#         total=2,
#         page=1,
#         size=50,
#         pages=1,
#     )


def dummy_length_function(item_list) -> int:
    return 200


@router.get("")
async def get_users() -> Page[User]:
    # This code is meant to demonstrate a get response
    # feel free to modify it for actual purposes as necessary

    page, size = parse_pagination_params()

    offset = (page - 1) * size

    fakeData = [
        User(userID=str(index), isMod=False, strikePoints=1)
        for index in range(offset, offset + size)
    ]

    return paginate(fakeData, length_function=dummy_length_function)
