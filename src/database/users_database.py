from . import DatabaseConnection
from .models import User
from typing import Optional
from settings import get_settings

settings = get_settings()


def get_user(discord_user_id: int) -> Optional[User]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT u.userid, u.discordUserId, u.discordGuildId, u.isMod FROM users u
        where u.discorduserid = %s
        """

        params = (str(discord_user_id),)

        cursor.execute(query, params)

        res = cursor.fetchone()

        if res:
            return User(res[0], res[1], res[2], res[3])


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
