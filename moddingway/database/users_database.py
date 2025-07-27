import logging
from typing import Optional

from moddingway.constants import UserRole
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
        u.userid, u.discordUserId, u.discordGuildId, u.userRole, u.temporaryPoints, u.permanentPoints, u.lastInfractionTimestamp, u.isBanned
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
                user_role=res[3],
                temporary_points=res[4],
                permanent_points=res[5],
                last_infraction_timestamp=res[6],
                is_banned=res[7],
            )


def get_users(limit: int, offset: int) -> list[User]:
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
                    user_role=row[3],
                    temporary_points=row[4],
                    permanent_points=row[5],
                    last_infraction_timestamp=row[6],
                    is_banned=row[7],
                )
                for row in res
            ]
        return []


def add_user(discord_user_id: int) -> User:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
            INSERT INTO users (discordUserId, discordGuildId)
            VALUES (%s, %s)
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
            user_role=UserRole.USER,
            temporary_points=0,
            permanent_points=0,
            is_banned=False,
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


def decrement_user_strike_points(
    user_id: int, temporary_point_amount: int, permanent_point_amount: int
):
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
            UPDATE users SET
            temporarypoints = GREATEST(temporarypoints - %s, 0),
            permanentPoints = GREATEST(permanentPoints - %s, 0)
            WHERE userID = %s
        """

        params = (
            temporary_point_amount,
            permanent_point_amount,
            user_id,
        )
        cursor.execute(query, params)


def get_mod_count() -> int:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:

        query = """
            SELECT COUNT(*)
            FROM users
            WHERE user_role = %s
        """
        params = (2,)
        cursor.execute(query, params)

        result = cursor.fetchall()
        return result[0][0]


def get_mods(limit: int, offset: int) -> list[User]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT * FROM users
        WHERE user_role = %s
        LIMIT %s OFFSET %s;
        """

        params = (2, limit, offset)

        cursor.execute(query, params)

        res = cursor.fetchall()

        if res:
            return [
                User(
                    user_id=row[0],
                    discord_user_id=row[1],
                    discord_guild_id=row[2],
                    user_role=row[3],
                    temporary_points=row[4],
                    permanent_points=row[5],
                    last_infraction_timestamp=row[6],
                )
                for row in res
            ]
        return []


def update_user(user: User):
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
            UPDATE users
            SET temporaryPoints = %s,
            permanentPoints = %s,
            lastInfractionTimestamp = %s,
            isBanned = %s
            WHERE userId = %s
        """

        params = (
            user.temporary_points,
            user.permanent_points,
            user.last_infraction_timestamp,
            user.is_banned,
            user.user_id,
        )

        cursor.execute(query, params)


def get_banned_users(limit: int, offset: int) -> list[User]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT * FROM users
        WHERE isBanned = %s
        LIMIT %s OFFSET %s;
        """

        params = (True, limit, offset)

        cursor.execute(query, params)

        res = cursor.fetchall()

        if res:
            return [
                User(
                    user_id=row[0],
                    discord_user_id=row[1],
                    discord_guild_id=row[2],
                    user_role=row[3],
                    temporary_points=row[4],
                    permanent_points=row[5],
                    last_infraction_timestamp=row[6],
                    is_banned=row[7],
                )
                for row in res
            ]
        return []


def get_banned_count() -> int:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:

        query = """
            SELECT COUNT(*)
            FROM users
            WHERE isBanned = %s
        """
        params = (True,)
        cursor.execute(query, params)

        result = cursor.fetchall()
        return result[0][0]
