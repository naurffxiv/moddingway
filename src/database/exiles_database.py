from . import DatabaseConnection
from .models import Exile


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
