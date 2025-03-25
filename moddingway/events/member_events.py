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
)

settings = get_settings()
logger = logging.getLogger(__name__)


async def on_member_join(member):
    """
    Event handler for when a new member joins the server.
    Automatically assigns the NON_VERIFIED role and logs the action.
    """
    guild = member.guild

    # Get the logging channel from settings
    log_channel = guild.get_channel(settings.logging_channel_id)

    # Log an error if the channel doesn't exist
    if log_channel is None:
        logger.error(
            f"Logging channel {settings.logging_channel_id} not found. Member join event will not be logged to Discord."
        )

        # If we don't have a logging channel, at least perform the role assignment
        try:
            # Find the role by name using the enum value
            role = discord.utils.get(member.guild.roles, name=Role.NON_VERIFIED)

            if role:
                # Assign the role to the new member
                await member.add_roles(role)
                logger.info(
                    f"Successfully assigned {role.name} role to {member.display_name}"
                )
            else:
                logger.error(f"Role '{Role.NON_VERIFIED}' not found in the server.")
        except discord.Forbidden:
            logger.error(
                f"Bot does not have permission to add roles to {member.display_name}"
            )
        except Exception as e:
            logger.error(f"Failed to assign role: {str(e)}")

        return  # Exit early if no logging channel

    # Only create embed for logging if we have a valid channel
    async with create_interaction_embed_context(
        log_channel,
        user=member,
        description=f"<@{member.id}> joined the server",
        timestamp=datetime.now(timezone.utc),
        footer="Member Joined",
    ) as embed:
        try:
            # Find the role by name using the enum value
            role = discord.utils.get(member.guild.roles, name=Role.NON_VERIFIED)

            if role:
                # Assign the role to the new member
                await member.add_roles(role)
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
                log_info_and_add_field(
                    embed,
                    logger,
                    "Error",
                    f"Role '{Role.NON_VERIFIED}' not found in the server.",
                )
        except discord.Forbidden:
            log_info_and_add_field(
                embed,
                logger,
                "Error",
                f"Bot does not have permission to add roles to {member.display_name}",
            )
        except Exception as e:
            log_info_and_add_field(
                embed, logger, "Error", f"Failed to assign role: {str(e)}"
            )


async def on_member_remove(member):
    """
    Event handler for when a member leaves the server.
    Logs the member's departure including their roles and join date.
    """
    guild = member.guild

    # Get the logging channel from settings
    log_channel = guild.get_channel(settings.logging_channel_id)

    # Log an error if the channel doesn't exist
    if log_channel is None:
        logger.error(
            f"Logging channel {settings.logging_channel_id} not found. Member leave event will not be logged to Discord."
        )
        # If we don't have a logging channel, just log the departure to console
        logger.info(f"Member left: {member.display_name} ({member.id})")
        return

    async with create_interaction_embed_context(
        log_channel,
        user=member,
        description=f"<@{member.id}> left the server",
        timestamp=datetime.now(timezone.utc),
        footer="Member Left",
    ) as embed:
        try:
            # Calculate how long the member was in the server
            joined_at = member.joined_at
            if joined_at:
                joined_at = joined_at.replace(tzinfo=timezone.utc)
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
                for role in member.roles:
                    if role.name != "@everyone":
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
