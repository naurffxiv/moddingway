from typing import Optional
from fastapi import APIRouter
from moddingway_api.utils.paginate import parse_pagination_params, paginate
from fastapi_pagination import Page
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

@router.get("")
async def get_users() -> Page[User]:

    page, size = parse_pagination_params()
    limit = size
    offset = (page-1) * size

    db_user_list = users_database.get_users(limit, offset)
    total_count = users_database.get_user_count()

    user_list = [
        User(
            userID=str(db_user.user_id),
            isMod=db_user.is_mod,
            strikePoints=db_user.get_strike_points()
        )
        for db_user in db_user_list
    ]

    return paginate(user_list, length_function=lambda _: total_count)