from . import DatabaseConnection
from .models import Strike


def add_strike(strike: Strike) -> int:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
            INSERT INTO strikes
            (userID, severity, reason, createdTimestamp, createdBy, lastEditedTimestamp, lastEditedBy)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s)
            RETURNING strikeId
        """

        params = (
            strike.user_id,
            strike.severity,
            strike.reason,
            strike.created_timestamp,
            strike.created_by,
            strike.last_edited_timestamp,
            strike.last_edited_by,
        )

        cursor.execute(query, params)
        res = cursor.fetchone()

        return res[0]
