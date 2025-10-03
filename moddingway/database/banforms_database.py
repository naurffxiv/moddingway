import logging
from typing import Optional
from moddingway.settings import get_settings

from . import DatabaseConnection
from .models import BanForm, User

settings = get_settings()

logger = logging.getLogger(__name__)

def get_ban_forms(limit: int, offset: int) -> list[BanForm]:
    conn=DatabaseConnection()

    with conn.get_cursor as cursor:
        query = """
        SELECT * FROM forms
        LIMIT %s OFFSET %s;
        """
        params = (limit, offset)

        cursor.execute(query, params)

        res = cursor.fetchall()
        
        if res:
            return[
                BanForm(
                    form_id=row[0],
                    user_id = row[1],
                    reason=row[2],
                    approval=row[3],
                    approved_by=row[4],
                    submission_timestamp=row[5],
                )
                for row in res
            ]
        return []

def get_ban_form(form_id: int) -> Optional[BanForm]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT
        f.formID, f.userID, f.reason, f.approval, f.approvedByUserID, f.createdTimestamp
        FROM forms f
        where f.formID = %s
        """

        params = (str(form_id),)

        cursor.execute(query, params)

        res = cursor.fetchone()

        if res:
            return BanForm(
                    form_id=res[0],
                    user_id = res[1],
                    reason=res[2],
                    approval=res[3],
                    approved_by=res[4],
                    submission_timestamp=res[5],
                )
        
def get_form_count() -> int:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:

        query = """
            SELECT COUNT(*)
            FROM forms
        """

        cursor.execute(query)

        result = cursor.fetchall()
        return result[0][0]

def add_form(form: BanForm) -> int:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        INSERT INTO forms (userID, reason, createdTimestamp)
        VALUES (%s, %s, %s)
        RETURNING formID
        """

        params = (
            form.user_id,
            form.reason,
            form.submission_timestamp,
        )

        cursor.execute(query, params)
        res = cursor.fetchone()

        return res[0]
    
def update_form(form_id, approval, approved_by) -> tuple[bool,int]:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        UPDATE forms
        SET approval = %s, approvedByUserID = %s
        WHERE formID = %s
        """

        params = (
            approval,
            approved_by,
            form_id,
        )

        cursor.execute(query, params)

        query = """
        SELECT f.approval, f.formID
        FROM forms f
        WHERE formID = {form_id}
        """

        cursor.execute(query)
        res = cursor.fetchone()

        return res
    

# used to get discordUserId to unban user when banform approved    
def get_user_from_form(form_id) -> str:
    conn = DatabaseConnection()

    with conn.get_cursor() as cursor:
        query = """
        SELECT
        u.discordUserId
        FROM users u
        JOIN forms f ON f.userID = u.userID
        WHERE f.formID = %s
        """

        params = (form_id,)

        cursor.execute(query, params)

        res = cursor.fetchone()

        if res:
            return res[0]