from . import DatabaseConnection
from .models import User
from typing import Optional
from settings import get_settings

settings = get_settings()


def get_user(discord_user_id: int) -> Optional[User]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT
        u.userid, u.discordUserId, u.discordGuildId, u.isMod, u.temporaryPoints, u.permanentPoints, u.lastInfractionTimestamp
        FROM users u
        where u.discorduserid = %s
        """

        params = (str(discord_user_id),)

        cursor.execute(query, params)

        res = cursor.fetchone()

        if res:
            return User(
                user_id=res[0],
                discord_user_id=res[1],
                discord_guild_id=res[2],
                is_mod=res[3],
                temporary_points=res[4],
                permanent_points=res[5],
                last_infraction_timestamp=res[6],
            )


def add_user(discord_user_id: int) -> int:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
            INSERT INTO users (discordUserId, discordGuildId, isMod)
            VALUES (%s, %s, false)
            RETURNING userId
        """

        params = (str(discord_user_id), str(settings.guild_id))

        cursor.execute(query, params)

        res = cursor.fetchone()
        return res[0]
