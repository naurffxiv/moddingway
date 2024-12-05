from . import DatabaseConnection
from .models import Note
from typing import List


def add_note(note: Note) -> int:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
            INSERT INTO notes
            (userID, note, createdTimestamp, createdBy, lastEditedTimestamp, lastEditedBy)
            VALUES
            (%s, %s, %s, %s, %s, %s)
            RETURNING noteId
        """

        params = (
            note.user_id,
            note.note,
            note.created_timestamp,
            note.created_by,
            note.last_edited_timestamp,
            note.last_edited_by,
        )

        cursor.execute(query, params)
        res = cursor.fetchone()

        return res[0]
