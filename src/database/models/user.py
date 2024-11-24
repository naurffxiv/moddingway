from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from settings import get_settings

settings = get_settings()


class User(BaseModel):
    user_id: int
    discord_user_id: str
    discord_guild_id: str
    is_mod: bool
    temporary_points: int
    permanent_points: int
    last_infraction_timestamp: Optional[datetime]


def create_empty_user(user_id, discord_user_id, is_mod=False) -> User:
    return User(
        user_id=user_id,
        discord_user_id=discord_user_id,
        discord_guild_id=settings.guild_id,
        is_mod=is_mod,
        temporary_points=0,
        permanent_points=0,
        last_infraction_timestamp=None,
    )
