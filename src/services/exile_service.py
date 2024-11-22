import discord
import logging
from util import log_info_and_embed, add_and_remove_role, send_dm, user_has_role
from enums import Role, ExileStatus
from database import users_database, exiles_database
from typing import Optional
import datetime
from database.models import Exile, User
from datetime import timezone

logger = logging.getLogger(__name__)


async def exile_user(
    logging_embed: discord.Embed,
    user: discord.Member,
    duration: datetime.timedelta,
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
    end_timestamp = start_timestamp + duration
    exile_status = ExileStatus.TIMED_EXILED

    # create utc timestamp for exile end
    timestamp = int(end_timestamp.replace(tzinfo=timezone.utc).timestamp())

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
    try:
        await send_dm(
            user,
            f"You are being exiled from NA Ultimate Raiding - FFXIV.\n**Reason:** {reason}\nExile expires <t:{timestamp}:R>",
        )
    except Exception as e:
        log_info_and_embed(
            logging_embed, logger, f"Failed to send DM to exiled user, {e}"
        )

    log_info_and_embed(logging_embed, logger, f"<@{user.id}> was successfully exiled")


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

    # message user
    try:
        await send_dm(
            user,
            f"You have been un-exiled from NA Ultimate Raiding - FFXIV.",
        )
    except Exception as e:
        log_info_and_embed(
            logging_embed, logger, f"Failed to send DM to exiled user, {e}"
        )

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

    exile = exiles_database.get_user_active_exile(db_user.user_id)

    if exile is None:
        # This should only happen when someone was manually exiled then unexiled through the bot
        logger.info(
            f"No active exile associated with user ID {db_user.user_id} was found. Skipping DB actions..."
        )
    else:
        exiles_database.update_exile_status(exile.exile_id, ExileStatus.UNEXILED)
        logging_embed.set_footer(text=f"Exile ID: {exile.exile_id}")

    log_info_and_embed(logging_embed, logger, f"<@{user.id}> was successfully unexiled")


TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


async def get_user_exiles(logging_embed: discord.Embed, user: discord.User) -> str:
    db_user = users_database.get_user(user.id)
    if db_user is None:
        return "User not found in database"

    exile_list = exiles_database.get_user_exiles(db_user.user_id)

    if len(exile_list) == 0:
        return "No exiles found for user"

    result = f"Exiles found for <@{user.id}>:"
    for exile in exile_list:
        exile_id = exile[0]
        exile_reason = exile[1]
        exile_start_date = exile[2].strftime(TIME_FORMAT)
        exile_end_date = exile[3].strftime(TIME_FORMAT) if exile[3] else "Indefinite"
        exile_type = ExileStatus(exile[4]).name

        result = (
            result
            + f"\n* ID: {exile_id} | START DATE: {exile_start_date} | END DATE: {exile_end_date} | TYPE: {exile_type} | REASON: {exile_reason}"
        )

    return result
