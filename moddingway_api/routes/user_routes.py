from typing import Optional

from fastapi import APIRouter

from moddingway_api.schemas.user_schema import User

router = APIRouter(prefix="/users")


@router.get("/{user_id}")
async def get_user_by_id(user_id: int) -> Optional[User]:
    # This code is meant to demonstrate a get response
    # feel free to modify it for actual purposes as necessary
    return User(userID=str(user_id), isMod=False, strikePoints=1)
