from . import DatabaseConnection
from .models import Exile, PendingExile
from enums import ExileStatus
from datetime import datetime, timezone


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
        SELECT e.exileID, u.discordUserID, e.endTimestamp
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

def get_user_exiles(user_id) -> PendingExile:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT e.exileID, e.reason, e.startTimestamp, e.endTimestamp, e.exileStatus
        FROM exiles e
        JOIN users u ON e.userID = u.userID
        WHERE u.userID = %s;
        """

        params = (
            user_id,
        )

        cursor.execute(query, params)
        res = cursor.fetchall()

        return res