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


def list_notes(user_id: int) -> List[tuple]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        select n.noteid, n.note, n.createdby  
        from notes n
        join users u on u.userID = n.userID
        where u.userId = %s
        order by n.createdtimestamp asc
        """

        params = (user_id,)

        cursor.execute(query, params)
        res = cursor.fetchall()

        return res


def get_note(note_id: int) -> List[tuple]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        select n.noteid, n.note, n.createdby  
        from notes n
        join users u on u.userID = n.userID
        where n.noteid = %s
        """

        params = (note_id,)

        cursor.execute(query, params)
        res = cursor.fetchone()

        return res


def delete_note(note_id: int) -> List[tuple]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        delete from notes n
        where n.noteid = %s
        """
        params = (note_id,)

        cursor.execute(query, params)
        rows_affected = cursor.rowcount

        return rows_affected > 0
