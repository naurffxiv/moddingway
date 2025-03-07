import logging
from typing import Optional

from moddingway.settings import get_settings

from . import DatabaseConnection
from .models import User

settings = get_settings()

logger = logging.getLogger(__name__)


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

def get_users(limit:int, offset:int) -> list[User]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT * FROM users
        LIMIT %s OFFSET %s;
        """

        params = (limit, offset)

        cursor.execute(query, params)

        res = cursor.fetchall()

        if res:
            return [
                User(
                    user_id=row[0],
                    discord_user_id=row[1],
                    discord_guild_id=row[2],
                    is_mod=row[3],
                    temporary_points=row[4],
                    permanent_points=row[5],
                    last_infraction_timestamp=row[6],
                )
                for row in res
            ]
        return []


def add_user(discord_user_id: int) -> User:
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

        logger.info(f"Created user record in DB with id {res[0]}")
        return User(
            user_id=res[0],
            discord_user_id=str(discord_user_id),
            discord_guild_id=str(settings.guild_id),
            is_mod=False,
            temporary_points=0,
            permanent_points=0,
        )


def update_user_strike_points(user: User):
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
            UPDATE users
            SET temporaryPoints = %s,
            permanentPoints = %s,
            lastInfractionTimestamp = %s
            WHERE userId = %s
        """

        params = (
            user.temporary_points,
            user.permanent_points,
            user.last_infraction_timestamp,
            user.user_id,
        )

        cursor.execute(query, params)


def decrement_old_strike_points() -> int:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
            UPDATE users SET
            temporarypoints = temporarypoints - 1,
            lastinfractiontimestamp = lastinfractiontimestamp + INTERVAL '90 day'
            WHERE temporarypoints  > 0
            AND lastinfractiontimestamp < current_date - INTERVAL '90 day'
        """

        cursor.execute(query)

        return cursor.rowcount
    

def get_user_count() -> int:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:

        query = """
            SELECT COUNT(*)
            FROM users
        """

        cursor.execute(query)

        result = cursor.fetchall()
        return result[0][0]