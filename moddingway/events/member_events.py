import logging
import discord
from datetime import datetime, timezone

from moddingway.enums import Role
from moddingway.settings import get_settings
from moddingway.util import (
    log_info_and_add_field,
    log_info_and_embed,
    create_interaction_embed_context,
    user_has_role,
    find_and_assign_role,
    get_log_channel,
)

settings = get_settings()
logger = logging.getLogger(__name__)


async def on_member_join(member):
    """
    Event handler for when a new member joins the server.
    Automatically assigns the NON_VERIFIED role and logs the action.
    """
    # First find and assign the role - this happens regardless of logging ability
    is_role_assigned, message, role = await find_and_assign_role(
        member, Role.NON_VERIFIED
    )

    # Log the join to console regardless of Discord logging success
    logger.info(f"Member joined: {member.display_name} ({member.id})")

    # Try to get the logging channel for event logging
    log_channel = await get_log_channel(member.guild)
    if log_channel is None:
        return  # Exit early if no logging channel

    # Try to create and send the embed
    try:
        async with create_interaction_embed_context(
            log_channel,
            user=member,
            description=f"<@{member.id}> joined the server",
            timestamp=datetime.now(timezone.utc),
            footer="Member Joined",
        ) as embed:
            if is_role_assigned:
                # Use the message directly from find_and_assign_role which now includes the role mention
                log_info_and_add_field(embed, logger, "Result", message)

                # Add additional field with account creation date
                account_age = datetime.now(timezone.utc) - member.created_at.replace(
                    tzinfo=timezone.utc
                )
                account_age_days = account_age.days
                log_info_and_add_field(
                    embed,
                    logger,
                    "Account Age",
                    f"{account_age_days} days (Created: {member.created_at.strftime('%Y-%m-%d')})",
                )
            else:
                # If role assignment failed, log the error message
                log_info_and_add_field(embed, logger, "Error", message)
    except Exception as e:
        # If anything fails with the embed or sending, log to console
        logger.error(f"Failed to log member join to Discord: {str(e)}")
