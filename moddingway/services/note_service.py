import discord
import logging
from moddingway.database import users_database
from moddingway.util import log_info_and_embed, log_info_and_add_field
from moddingway.database import notes_database, users_database
from moddingway.database.models import Note
from datetime import datetime

logger = logging.getLogger(__name__)


async def add_note(
    logging_embed: discord.Embed,
    user: discord.Member,
    note: str,
    author: discord.Member,
):
    # find user in DB
    db_user = users_database.get_user(user.id)
    if db_user is None:
        log_info_and_embed(
            logging_embed,
            logger,
            "User not found in database, creating new record",
        )
        db_user = users_database.add_user(user.id)

    # create note
    note_timestamp = datetime.now()
    note = Note(
        user_id=db_user.user_id,
        note=note,
        created_timestamp=note_timestamp,
        created_by=str(author.id),
        last_edited_timestamp=note_timestamp,
        last_edited_by=str(author.id),
    )
    note.note_id = notes_database.add_note(note)
    logging_embed.set_footer(text=f"Note ID: {note.note_id}")

    log_info_and_add_field(
        logging_embed,
        logger,
        "Result",
        f"<@{user.id}> was given a note",
    )


async def get_user_notes(
    user: discord.Member,
) -> str:
    db_user = users_database.get_user(user.id)
    if db_user is None:
        return "User not found in database"

    note_list = notes_database.list_notes(db_user.user_id)
    logger.debug(note_list)

    if len(note_list) == 0:
        return "No notes found for user"
    result = f"Notes found for <@{user.id}>:"
    for note in note_list:
        result = (
            result
            + f"\n* ID: {note.note_id} | Note Creator: <@{note.created_by}> | Last Editor: <@{note.last_editor}> | Note: {note.content}"
        )

    return result
