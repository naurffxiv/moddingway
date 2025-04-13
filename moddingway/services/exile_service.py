import datetime
import logging
import re
from datetime import timezone
from typing import Optional

import discord

from moddingway.database import exiles_database, users_database, roles_database
from moddingway.database.models import Exile
from moddingway.enums import ExileStatus, Role
from moddingway.settings import get_settings
from moddingway.util import (
    add_and_remove_role,
    log_info_and_add_field,
    log_info_and_embed,
    send_dm,
    timestamp_to_epoch,
    find_or_create_user,
)
from moddingway import util

settings = get_settings()
logger = logging.getLogger(__name__)


async def exile_user(
    logging_embed: discord.Embed,
    user: discord.Member,
    duration: datetime.timedelta,
    reason: str,
) -> Optional[str]:
    db_user = users_database.get_user(user.id)
    if db_user:
        currentExile = exiles_database.get_user_active_exile(db_user.user_id)
        if not util.user_has_role(user, Role.VERIFIED) and currentExile:
            new_endTimestamp = currentExile.end_timestamp + duration
            exiles_database.update_exile_end(currentExile.exile_id, new_endTimestamp)
            log_info_and_add_field(
                logging_embed,
                logger,
                "Result",
                f"Exile extended until <t:{timestamp_to_epoch(new_endTimestamp)}>",
            )
            return "User exile extended"

    if not util.user_has_role(user, Role.VERIFIED):
        error_message = "User is not currently verified, no action will be taken"
        log_info_and_add_field(
            logging_embed,
            logger,
            "Error",
            error_message,
        )
        return error_message

    # Replace the manual user lookup and creation with the helper method
    db_user = await find_or_create_user(user.id, logging_embed)

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

    roles_to_save: list[Role] = []

    # change user role
    await add_and_remove_role(
        user, role_to_add=Role.EXILED, role_to_remove=Role.VERIFIED
    )

    # check for any sticky roles to strip
    try:
        for role in user.roles:
            if role.id in settings.sticky_roles:
                discord_role = user.guild.get_role(role.id)
                if discord_role is not None:
                    roles_to_save.append(user.guild.get_role(discord_role.id))

        if len(roles_to_save) > 0:
            await user.remove_roles(*roles_to_save)
            roles_database.add_sticky_roles(
                db_user.user_id, [role.id for role in roles_to_save]
            )
    except Exception as e:
        log_info_and_add_field(
            logging_embed,
            logger,
            "Error",
            f"Sticky roles could not be completely removed, {e}",
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
        "Expiration",
        f"<t:{timestamp_to_epoch(end_timestamp)}:R>",
    )
    log_info_and_add_field(
        logging_embed,
        logger,
        "Result",
        f"<@{user.id}> was successfully exiled",
    )


async def unexile_user(
    logging_embed: discord.Embed, user: discord.Member
) -> Optional[str]:
    if not util.user_has_role(user, Role.EXILED):
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

    # check for any sticky roles to restore
    try:
        roles_to_restore: list[Role] = []
        for role in roles_database.get_sticky_roles(db_user.user_id):
            discord_role = user.guild.get_role(int(role))
            if discord_role is not None:
                roles_to_restore.append(discord_role)
            else:
                logger.error("Role %s was not found in the server, skipping...", role)

        if len(roles_to_restore) > 0:
            await user.add_roles(*roles_to_restore)
            roles_database.remove_sticky_roles(db_user.user_id)
    except Exception as e:
        log_info_and_add_field(
            logging_embed,
            logger,
            "Error",
            f"Sticky roles could not be completely removed, {e}",
        )

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
            exile_start_epoch = timestamp_to_epoch(exile.start_timestamp)
            exile_end_epoch = (
                timestamp_to_epoch(exile.end_timestamp) if exile.exile_status else None
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
