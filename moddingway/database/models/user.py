from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from moddingway.settings import get_settings

settings = get_settings()


class User(BaseModel):
    user_id: int
    discord_user_id: str
    discord_guild_id: str
    is_mod: bool
    temporary_points: int
    permanent_points: int
    last_infraction_timestamp: Optional[datetime] = None
    is_banned: bool

    def get_strike_points(self) -> int:
        return self.temporary_points + self.permanent_points
