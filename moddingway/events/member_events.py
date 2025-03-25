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


async def on_member_remove(member):
    """
    Event handler for when a member leaves the server.
    Logs the member's departure including their roles and join date.
    """
    # Log basic info to console regardless of logging channel
    logger.info(f"Member left: {member.display_name} ({member.id})")

    # Get the logging channel
    log_channel = await get_log_channel(member.guild)
    if log_channel is None:
        return  # Exit early if no logging channel

    # Create log embed
    async with create_interaction_embed_context(
        log_channel,
        user=member,
        description=f"<@{member.id}> left the server",
        timestamp=datetime.now(timezone.utc),
        footer="Member Left",
    ) as embed:
        try:
            # Calculate how long the member was in the server
            joined_at = member.joined_at.replace(tzinfo=timezone.utc)
            time_in_server = datetime.now(timezone.utc) - joined_at
            days_in_server = time_in_server.days
            log_info_and_add_field(
                embed,
                logger,
                "Time in Server",
                f"{days_in_server} days (Joined: {joined_at.strftime('%Y-%m-%d')})",
            )

            # List the roles the member had
            if member.roles:
                role_mentions = []
                valid_role_names = [
                    role.value for role in Role
                ]  # Get all values from your Role enum

                for role in member.roles:
                    if role.name in valid_role_names:
                        role_mentions.append(f"<@&{role.id}>")

                if role_mentions:
                    log_info_and_add_field(
                        embed, logger, "Roles", " ".join(role_mentions)
                    )

            # Add account creation date for reference
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

        except Exception as e:
            log_info_and_add_field(
                embed, logger, "Error", f"Error logging member departure: {str(e)}"
            )
