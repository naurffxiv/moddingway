from . import DatabaseConnection
from .models import Strike
from typing import List


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


def list_strikes(user_id: int) -> List[tuple]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        select s.strikeid, s.severity, s.reason, s.createdby  
        from strikes s
        join users u on u.userID = s.userID
        where u.userId = %s
        order by s.createdtimestamp asc
        """

        params = (user_id,)

        cursor.execute(query, params)
        res = cursor.fetchall()

        return res
