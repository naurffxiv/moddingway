from fastapi_pagination import Page
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from moddingway.settings import get_settings
from moddingway_api.schemas.banned_user_schema import Banned
from moddingway_api.utils.paginate import parse_pagination_params, paginate
from moddingway.database import users_database


router = APIRouter(prefix="/bannedusers")
settings = get_settings()


@router.get("")
async def get_banned_users() -> Page[Banned]:

    page, size = parse_pagination_params()
    limit = size
    offset = (page - 1) * size

    db_banned_list = users_database.get_banned_users(limit, offset)
    total_count = users_database.get_banned_count()

    banned_list = [
        Banned(userID=str(db_banned.user_id)) for db_banned in db_banned_list
    ]

    return paginate(banned_list, length_function=lambda _: total_count)


class BanRequest(BaseModel):
    user_id: str  # discord user ID
    reason: Optional[str] = "Banned via API"  # optional reason shown in audit
    delete_message_days: Optional[int] = 0  # optional to delete message (0-7 days)


@router.post("")
async def ban_user(request: BanRequest):
    url = (
        f"https://discord.com/api/v10/guilds/{settings.guild_id}/bans/{request.user_id}"
    )
    headers = {"Authorization": f"Bot {settings.discord_token}"}
    body = {
        "reason": request.reason,
        "delete_message_days": request.delete_message_days,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers, json=body)
            response.raise_for_status()  # will raise if ban fails
            return {"detail": f"User {request.user_id} has been banned"}
    except (httpx.HTTPError, httpx.RequestError) as exc:
        raise HTTPException(status_code=503, detail=str(exc))
