import discord
import logging
from typing import Optional
import datetime
from datetime import timezone
import re
from moddingway.util import (
    log_info_and_add_field,
    log_info_and_embed,
    add_and_remove_role,
    send_dm,
    user_has_role,
)
from moddingway.enums import Role, ExileStatus
from moddingway.database import users_database, exiles_database
from moddingway.database.models import Exile


logger = logging.getLogger(__name__)


async def exile_user(
    logging_embed: discord.Embed,
    user: discord.Member,
    duration: datetime.timedelta,
    reason: str,
    interaction: discord.Interaction,
) -> Optional[str]:
    if not user_has_role(user, Role.VERIFIED):
        error_message = "User is not currently verified, no action will be taken"
        log_info_and_add_field(
            logging_embed,
            logger,
            "Error",
            error_message,
        )
        return error_message
    if user.top_role >= interaction.user.top_role:
        error_message = f"Unable to exile {user.mention}: You cannot exile a user with an equal or higher role than yourself."
        log_info_and_add_field(
            logging_embed,
            logger,
            "Error",
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
        db_user = users_database.add_user(user.id)

    # add exile entry into DB
    start_timestamp = datetime.datetime.now(datetime.timezone.utc)
    end_timestamp = start_timestamp + duration
    exile_status = ExileStatus.TIMED_EXILED

    # create utc timestamp for exile end
    timestamp = int(end_timestamp.replace(tzinfo=timezone.utc).timestamp())

    exile = Exile(
        exile_id=None,
        user_id=db_user.user_id,
        discord_id=user.id,
        reason=reason,
        exile_status=exile_status.value,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
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
            f"You are being exiled from NA Ultimate Raiding - FFXIV.\n**Reason:** {reason}\nExile expiration: <t:{timestamp}:R>",
        )
    except Exception as e:
        log_info_and_add_field(
            logging_embed, logger, "DM Status", f"Failed to send DM to exiled user, {e}"
        )

    log_info_and_add_field(
        logging_embed,
        logger,
        "Result",
        f"<@{user.id}> was successfully exiled",
    )


async def unexile_user(
    logging_embed: discord.Embed, user: discord.User
) -> Optional[str]:
    if not user_has_role(user, Role.EXILED):
        error_message = "User is not currently exiled, no action will be taken"
        log_info_and_add_field(
            logging_embed,
            logger,
            "Error",
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
        log_info_and_add_field(
            logging_embed, logger, "DM Status", f"Failed to send DM to exiled user, {e}"
        )

    # update exile record
    db_user = users_database.get_user(user.id)
    if db_user is None:
        error_message = (
            "User has been unexiled, but no user record was found in the database"
        )
        log_info_and_add_field(
            logging_embed,
            logger,
            "Error",
            error_message,
        )
        return error_message

    exile = exiles_database.get_user_active_exile(db_user.user_id)

    if exile is None:
        # This should only happen when someone was manually exiled then unexiled through the bot
        logger.info(
            f"No active exile associated with user ID {db_user.user_id} was found. Skipping DB actions..."
        )
    else:
        exiles_database.update_exile_status(exile.exile_id, ExileStatus.UNEXILED)
        logging_embed.set_footer(text=f"Exile ID: {exile.exile_id}")

    log_info_and_add_field(
        logging_embed, logger, "Result", f"<@{user.id}> was successfully unexiled"
    )


TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


async def get_user_exiles(user: discord.User) -> str:
    db_user = users_database.get_user(user.id)
    if db_user is None:
        return "User not found in database"

    exile_list = exiles_database.get_user_exiles(db_user.user_id)

    if len(exile_list) == 0:
        return "No exiles found for user"
    else:
        result = f"Exiles found for <@{user.id}>:"
        for exile in exile_list:
            exile_id = exile.exile_id
            exile_reason = exile.reason
            exile_start_epoch = round(exile.start_timestamp.timestamp())
            exile_end_epoch = (
                round(exile.end_timestamp.timestamp()) if exile.exile_status else None
            )
            exile_start_date = f"<t:{exile_start_epoch}:F>"
            exile_end_date = (
                f"<t:{exile_end_epoch}:F>" if exile_end_epoch else "Indefinite"
            )
            exile_type = ExileStatus(exile.exile_status).name

            result = (
                result
                + f"\n* ID: {exile_id} | START DATE: {exile_start_date} | END DATE: {exile_end_date} | TYPE: {exile_type} | REASON: {exile_reason}"
            )

    return result


async def get_active_exiles() -> str:
    exile_list = exiles_database.get_all_active_exiles()
    logger.info("Database query completed.")
    if len(exile_list) == 0:
        return "No active exiles found"

    result = f"Active exiles found for"
    for exile in exile_list:
        logger.info(type(exile))
        exile_id = exile.exile_id
        discord_id = f"<@{exile.discord_id}>"
        exile_reason = exile.reason
        exile_start_epoch = round(exile.start_timestamp.timestamp())
        exile_end_epoch = (
            round(exile.end_timestamp.timestamp()) if exile.exile_status else None
        )
        exile_start_date = f"<t:{exile_start_epoch}:F>"
        exile_end_date = f"<t:{exile_end_epoch}:F>" if exile_end_epoch else "Indefinite"
        exile_type = ExileStatus(exile.exile_status).name

        result = (
            result
            + f"\n* ID: {exile_id} | USER: {discord_id} | START DATE: {exile_start_date} | END DATE: {exile_end_date} | TYPE: {exile_type} | REASON: {exile_reason}"
        )

    return result


def format_time_string(duration_string: str):
    if not duration_string:
        return None
    regex = "^(\d\d?)(sec|min|min|hour|day)"  # Matches (digit, digit?)(option of [sec, min, hour, day])
    result = re.search(regex, duration_string)
    if result:
        duration = int(result.group(1))
        unit = result.group(2)
        p_unit = None

        if unit == "sec":
            p_unit = "second"
        elif unit == "min":
            p_unit = "minute"
        else:
            p_unit = unit

        if duration != 1:
            p_unit += "s"

        return result.group(1) + " " + p_unit
    return None
