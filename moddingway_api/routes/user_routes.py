from typing import Optional

from fastapi import APIRouter
from fastapi_pagination import Page, paginate, create_page, Params

from moddingway.database import users_database
from moddingway_api.schemas.user_schema import User, UserPage

router = APIRouter(prefix="/users")


@router.get("/{user_id}")
async def get_user_by_id(user_id: int) -> Optional[User]:

    db_user = users_database.get_user(user_id)
    user = User(
        userID = str(db_user.user_id),
        isMod = db_user.is_mod,
        strikePoints = db_user.get_strike_points()
    )
    return user


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


@router.get("")
async def get_users(page: int = 1, size: int = 50) -> UserPage:

    limit = size
    offset = (page-1) * size
    db_user_list = users_database.get_users(limit, offset)
    db_user_count = users_database.get_user_count()

    user_list = [
        User(
            userID=str(db_user.user_id),
            isMod=db_user.is_mod,
            strikePoints=db_user.get_strike_points()
        )
        for db_user in db_user_list
    ]

    total_pages = (db_user_count + size - 1) // size
    
    return UserPage(
        items=user_list,
        total=db_user_count,
        page=page,
        size=size,
        pages=total_pages
    )
