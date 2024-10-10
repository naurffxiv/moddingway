import discord
import logging
from util import log_info_and_embed, add_and_remove_role, send_dm, user_has_role
from enums import Role, ExileStatus
from database import users_database, exiles_database
from typing import Optional
import datetime
from database.models import Exile, User

logger = logging.getLogger(__name__)


async def exile_user(
    logging_embed: discord.Embed,
    user: discord.Member,
    duration: Optional[datetime.timedelta],
    reason: str,
) -> Optional[str]:
    if not user_has_role(user, Role.VERIFIED):
        error_message = "User is not currently verified, no action will be taken"
        log_info_and_embed(
            logging_embed,
            logger,
            error_message,
        )
        return error_message

    # look up user in DB
    db_user = users_database.get_user(user.id)
    if db_user is None:
        log_info_and_embed(
            logging_embed,
            logger,
            f"User not found in database, creating new record",
        )
        db_user_id = users_database.add_user(user.id)
        logger.info(f"Created user record in DB with id {db_user_id}")

        db_user = User(db_user_id, user.id, None, None)

    # add exile entry into DB
    start_timestamp = datetime.datetime.now(datetime.timezone.utc)
    end_timestamp = None
    exile_status = ExileStatus.INDEFINITE_EXILE
    if duration:
        end_timestamp = start_timestamp + duration
        exile_status = ExileStatus.TIMED_EXILED

    exile = Exile(
        None,
        db_user.user_id,
        reason,
        exile_status.value,
        start_timestamp,
        end_timestamp,
    )
    exile_id = exiles_database.add_exile(exile)

    logger.info(f"Created exile with ID {exile_id}")
    logging_embed.set_footer(text=f"Exile ID: {exile_id}")

    # change user role
    await add_and_remove_role(
        user, role_to_add=Role.EXILED, role_to_remove=Role.VERIFIED
    )

    # message user
    await send_dm(
        user,
        f"You are being exiled from NA Ultimate Raiding - FF XIV for the following reason: \n> {reason}",
    )


async def unexile_user(
    logging_embed: discord.Embed, user: discord.User
) -> Optional[str]:
    if not user_has_role(user, Role.EXILED):
        error_message = "User is not currently exiled, no action will be taken"
        log_info_and_embed(
            logging_embed,
            logger,
            error_message,
        )
        return error_message

    # unexile user
    await add_and_remove_role(user, Role.VERIFIED, Role.EXILED)

    # update exile record
    db_user = users_database.get_user(user.id)
    if db_user is None:
        log_info_and_embed(
            logging_embed,
            logger,
            f"User not found in database, creating new record",
        )
        db_user_id = users_database.add_user(user.id)
        log_info_and_embed(logging_embed, logger, f"User record created in database")

        db_user = User(db_user_id, user.id, None, None)

    exile_id = exiles_database.remove_user_exiles(db_user.user_id)
    logging_embed.set_footer(text=f"Exile ID: {exile_id}")
