from typing import Optional
from fastapi import APIRouter, HTTPException
from moddingway_api.utils.paginate import parse_pagination_params, paginate
from fastapi_pagination import Page
from moddingway.database import users_database
from moddingway.enums import UserRole
from moddingway_api.schemas.mod_schema import Mod

router = APIRouter(prefix="/mods")


@router.get("/{mod_id}")
async def get_mod_by_id(mod_id: int) -> Optional[Mod]:

    db_user = users_database.get_user(mod_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.has_mod_permissions():
        mod = Mod(modID=str(db_user.user_id))
        return mod
    else:
        raise HTTPException(status_code=404, detail="Mod not found")


@router.get("")
async def get_mods() -> Page[Mod]:

    page, size = parse_pagination_params()
    limit = size
    offset = (page - 1) * size

    db_mod_list = users_database.get_mods(limit, offset)
    total_count = users_database.get_mod_count()

    mod_list = [Mod(modID=str(db_mod.user_id)) for db_mod in db_mod_list]

    return paginate(mod_list, length_function=lambda _: total_count)
