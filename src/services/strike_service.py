import discord
import logging
from enums import StrikeSeverity
from database import users_database
from util import log_info_and_embed, send_dm
from database import strikes_database, users_database
from database.models import Strike, User
from datetime import datetime, timedelta
from . import exile_service, ban_service
from constants import (
    MINOR_INFRACTION_POINTS,
    MODERATE_INFRACTION_POINTS,
    SERIOUS_INFRACTION_POINTS,
)

logger = logging.getLogger(__name__)


async def add_strike(
    logging_embed: discord.Embed,
    user: discord.Member,
    severity: StrikeSeverity,
    reason: str,
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

    # create strike
    strike_timestamp = datetime.now()
    strike = Strike(
        user_id=db_user.user_id,
        severity=severity,
        reason=reason,
        created_timestamp=strike_timestamp,
        created_by=author.id,
        last_edited_timestamp=strike_timestamp,
        last_edited_by=author.id,
    )
    strike.strike_id = strikes_database.add_strike(strike)
    logging_embed.set_footer(text=f"Strike ID: {strike.strike_id}")

    # increment user points, update
    db_user.last_infraction_timestamp = strike_timestamp
    previous_points = db_user.get_strike_points()
    _apply_strike_point_penalty(db_user, severity)
    users_database.update_user_strike_points(db_user)

    log_info_and_embed(
        logging_embed,
        logger,
        f"<@{user.id}> was given a strike, bringing them to {db_user.get_strike_points()} points",
    )

    punishment = await _apply_punishment(logging_embed, user, db_user, previous_points)
    logging_embed.add_field(name="Punishment", value=punishment)

    # message user
    try:
        await send_dm(
            user,
            f"Your actions in NA Ultimate Raiding - FFXIV resulted in a strike against your account. This may result in punishment depending on the frequency or severity of your strikes.\n**Reason:** {reason}",
        )
    except Exception as e:
        log_info_and_embed(
            logging_embed, logger, f"Failed to send DM to exiled user, {e}"
        )


async def get_user_strikes(
    logging_embed: discord.Embed,
    user: discord.Member,
) -> str:
    db_user = users_database.get_user(user.id)
    if db_user is None:
        return "User not found in database"

    strike_list = strikes_database.list_strikes(db_user.user_id)

    if len(strike_list) == 0:
        return "No exiles found for user"

    result = f"Strikes found for <@{user.id}>: [Temporary points: {db_user.temporary_points} | Permanent points: {db_user.permanent_points}]"
    for strike in strike_list:
        strike_id = strike[0]
        strike_severity = StrikeSeverity(strike[1])
        strike_reason = strike[2]
        strike_created_by = strike[3]

        result = (
            result
            + f"\n* ID: {strike_id} | SEVERITY: {strike_severity} | Moderator: <@{strike_created_by}> | REASON: {strike_reason}"
        )

    result = result + f"\nTotal Points: {db_user.get_strike_points()}"

    return result


def _apply_strike_point_penalty(db_user: User, severity: StrikeSeverity):
    match severity:
        case StrikeSeverity.MINOR:
            db_user.temporary_points = (
                db_user.temporary_points + MINOR_INFRACTION_POINTS
            )
        case StrikeSeverity.MODERATE:
            db_user.temporary_points = (
                db_user.temporary_points + MODERATE_INFRACTION_POINTS
            )
        case StrikeSeverity.SERIOUS:
            db_user.permanent_points = (
                db_user.permanent_points + SERIOUS_INFRACTION_POINTS
            )


async def _apply_punishment(
    logging_embed: discord.Embed,
    user: discord.Member,
    db_user: User,
    previous_points: int,
) -> str:
    total_points = db_user.get_strike_points()

    # TODO: MOD-93 known error, if an exiled user is given a strike, the follow up exile is not created
    exile_reason = (
        "Your actions were severe or frequent enough for you to receive this exile"
    )

    if total_points >= 15:
        punishment = "Permanent ban"
        await ban_service.ban_user(
            user,
            "Your strike were severe or frequent to be removed from NA Ultimate Raiding - FFXIV",
        )
    elif total_points >= 10 and previous_points < 10:
        punishment = "2 week exile"
        await exile_service.exile_user(
            logging_embed,
            user,
            timedelta(weeks=2),
            exile_reason,
        )
    elif total_points >= 7 and previous_points < 7:
        punishment = "1 week exile"
        await exile_service.exile_user(
            logging_embed,
            user,
            timedelta(weeks=1),
            exile_reason,
        )
    elif total_points >= 5 and previous_points < 5:
        punishment = "3 day exile"
        await exile_service.exile_user(
            logging_embed, user, timedelta(days=3), exile_reason
        )
    elif total_points >= 3 and previous_points < 3:
        punishment = "1 day exile"
        await exile_service.exile_user(
            logging_embed, user, timedelta(days=1), exile_reason
        )
    else:
        punishment = "Nothing"

    return punishment