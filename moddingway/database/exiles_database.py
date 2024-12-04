import logging
from datetime import datetime, timezone

from moddingway.enums import ExileStatus

from . import DatabaseConnection
from .models import Exile, PendingExile

logger = logging.getLogger(__name__)


def add_exile(exile: Exile) -> int:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        INSERT INTO exiles (userId, reason, exileStatus, startTimestamp, endTimestamp)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING exileId
        """

        params = (
            exile.user_id,
            exile.reason,
            exile.exile_status,
            exile.start_timestamp,
            exile.end_timestamp,
        )

        cursor.execute(query, params)
        res = cursor.fetchone()

        return res[0]


def update_exile_status(exile_id, exile_status):
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        UPDATE exiles
        SET exileStatus = %s
        WHERE exileID = %s
        """

        params = (
            exile_status,
            exile_id,
        )

        cursor.execute(query, params)

        return


def remove_user_exiles(user_id):
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        delete from exiles e where e.userId = %s returning e.exileId
        """

        params = (user_id,)

        cursor.execute(query, params)
        res = cursor.fetchone()

        if res is not None:
            return res[0]
        else:
            return None


def get_pending_unexiles() -> list[PendingExile]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT e.exileID, u.userID, u.discordUserID, e.endTimestamp
        FROM exiles e
        JOIN users u ON e.userID = u.userID
        WHERE e.exileStatus = %s AND e.endTimestamp < %s;
        """

        params = (
            ExileStatus.TIMED_EXILED,
            datetime.now(timezone.utc),
        )

        cursor.execute(query, params)
        res = cursor.fetchall()

        return [PendingExile(*x) for x in res]


def get_user_active_exile(user_id) -> PendingExile:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT e.exileID, u.userID, u.discordUserID, e.endTimestamp
        FROM exiles e
        JOIN users u ON e.userID = u.userID
        WHERE u.userID = %s AND  e.exileStatus = %s 
        LIMIT 1;
        """

        params = (user_id, ExileStatus.TIMED_EXILED)

        cursor.execute(query, params)
        res = cursor.fetchone()

        if res is not None:
            return PendingExile(*res)
        else:
            return None


#   exile_id, user_id, discord_id, reason, exile_status, start_timestamp, end_timestamp
def get_user_exiles(user_id) -> list[Exile]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT e.exileID, u.userID, u.discordUserID, e.reason, e.exileStatus, e.startTimestamp, e.endTimestamp
        FROM exiles e
        JOIN users u ON e.userID = u.userID
        WHERE u.userID = %s
        ORDER BY e.startTimestamp ASC;
        """

        params = (user_id,)

        cursor.execute(query, params)
        res = cursor.fetchall()

        if res is not None:
            return [Exile(*row) for row in res]  # Create a list of Exile objects
        else:
            return []


def get_all_active_exiles() -> list[Exile]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT e.exileID, u.userID, u.discordUserID, e.reason, e.exileStatus, e.startTimestamp, e.endTimestamp
        FROM exiles e
        JOIN users u ON e.userID = u.userID
        WHERE e.exileStatus = %s AND e.reason != 'roulette';
        """

        params = (ExileStatus.TIMED_EXILED,)

        cursor.execute(query, params)
        res = cursor.fetchall()

        if res is not None:
            return [Exile(*row) for row in res]  # Create a list of Exile objects
        else:
            return []
