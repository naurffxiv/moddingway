from . import DatabaseConnection
from discord import Role
import logging


logger = logging.getLogger(__name__)


def add_sticky_roles(user_id: int, roles: list[int]):
    if len(roles) == 0:
        return

    conn = DatabaseConnection()
    with conn.get_cursor() as cursor:
        query = "INSERT INTO roles (userID, roleID) VALUES "
        query += ",".join([f"({user_id}, {role})" for role in roles])
        logger.info(query)
        cursor.execute(query)

        return


def remove_sticky_roles(user_id: int):
    conn = DatabaseConnection()
    with conn.get_cursor() as cursor:
        query = """
            DELETE FROM roles WHERE userID = %s RETURNING roleID
        """

        params = (user_id,)

        cursor.execute(query, params)
        res = cursor.fetchall()

        return res


def get_sticky_roles(user_id: int):
    conn = DatabaseConnection()
    with conn.get_cursor() as cursor:
        query = """
            SELECT roleID FROM roles WHERE userID = %s
        """

        params = (user_id,)

        cursor.execute(query, params)
        res = cursor.fetchall()
        if res is not None:
            return [x[0] for x in res]
        else:
            return
