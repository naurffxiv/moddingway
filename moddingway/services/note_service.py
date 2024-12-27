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


async def get_note_by_id(
    note_id: int,
) -> str:
    db_note = notes_database.get_note(note_id)
    if db_note:
        return f"\n* ID: {db_note.note_id} | Note: {db_note.content} | Note Creator: <@{db_note.created_by}> | Last Editor: <@{db_note.last_editor}>"
    else:
        return


async def get_user_notes(
    user: discord.User,
) -> str:
    db_user = users_database.get_user(user.id)
    if db_user is None:
        return "User not found in database"

    note_list = notes_database.list_notes(db_user.user_id)

    if len(note_list) == 0:
        return f"No notes found for user <@{user.id}>"
    result = f"Notes found for <@{user.id}>:"
    for note in note_list:
        result = (
            result
            + f"\n* ID: {note.note_id} | Note Creator: <@{note.created_by}> | Last Editor: <@{note.last_editor}> | Note: {note.content}"
        )

    return result


async def delete_user_note(
    logging_embed: discord.Embed,
    note_id: int,
) -> str:
    note_row = notes_database.get_note(note_id)
    if note_row is None:
        log_info_and_add_field(
            logging_embed,
            logger,
            "Result",
            f"Note not found, no action will be taken",
        )
        return "Note not found in database, no action will be taken"

    result = notes_database.delete_note(note_id)

    if result:
        logging_embed.set_footer(text=f"Note ID: {note_id}")

        log_info_and_add_field(
            logging_embed,
            logger,
            "Result",
            f"Note deleted",
        )

        result = f"Successfully deleted note: {note_id}"
    else:
        log_info_and_add_field(
            logging_embed,
            logger,
            "Result",
            f"Error deleting note",
        )
        result = "There was an error deleting note from the database"

    return result


async def update_user_note(
    logging_embed: discord.Embed,
    last_author: discord.Member,
    new_note: str,
    note_id: int,
) -> str:
    db_note = notes_database.get_note(note_id)
    if db_note is None:
        log_info_and_add_field(
            logging_embed,
            logger,
            "Result",
            f"Note not found",
        )
        return "Note not found in database"
    old_note = db_note.content
    note_update_timestamp = datetime.now()
    result = notes_database.update_note(
        new_note, str(last_author.id), note_update_timestamp, note_id
    )
    if result:
        logging_embed.set_footer(text=f"Note ID: {note_id}")
        logging_embed.add_field(name="Old note", value=old_note)
        log_info_and_add_field(
            logging_embed,
            logger,
            "Result",
            f"Note updated",
        )
        return "Note succesfully updated"
    else:
        return "There was an error updating the note"
