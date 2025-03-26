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
    success, message, role = await find_and_assign_role(member, Role.NON_VERIFIED)

    # Then get the logging channel for event logging
    log_channel = await get_log_channel(member.guild)
    if log_channel is None:
        return  # Exit early if no logging channel

    # Create log embed
    async with create_interaction_embed_context(
        log_channel,
        user=member,
        description=f"<@{member.id}> joined the server",
        timestamp=datetime.now(timezone.utc),
        footer="Member Joined",
    ) as embed:
        if success:
            log_info_and_add_field(
                embed,
                logger,
                "Result",
                f"Successfully assigned <@&{role.id}> role to {member.display_name}",
            )

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
            # If role assignment failed, log the error
            log_info_and_add_field(embed, logger, "Error", message)
