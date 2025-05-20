import logging
from datetime import datetime, timezone
import discord

from discord import Guild, User
from discord.ext.commands import Bot

from moddingway.database import users_database
from moddingway.enums import Role
from moddingway.settings import get_settings
from moddingway.util import (
    create_interaction_embed_context,
    find_and_assign_role,
    get_log_channel,
    log_info_and_add_field,
)

settings = get_settings()
logger = logging.getLogger(__name__)


def register_events(bot: Bot):
    @bot.event
    async def on_member_join(member):
        """
        Event handler for when a new member joins the server.
        Automatically assigns the NON_VERIFIED role and logs the action.
        """
        # First find and assign the role - this happens regardless of logging ability
        is_role_assigned, message, role = await find_and_assign_role(
            member, Role.NON_VERIFIED
        )

        logger.info(f"Member joined: {member.display_name} ({member.id})")

        log_channel = get_log_channel(member.guild)
        if log_channel is None:
            return

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
                    log_info_and_add_field(embed, logger, "Result", message)
                    account_age = datetime.now(
                        timezone.utc
                    ) - member.created_at.replace(tzinfo=timezone.utc)
                    account_age_days = account_age.days
                    log_info_and_add_field(
                        embed,
                        logger,
                        "Account Age",
                        f"{account_age_days} days (Created: {member.created_at.strftime('%Y-%m-%d')})",
                    )
                else:
                    log_info_and_add_field(embed, logger, "Error", message)
        except Exception as e:
            logger.error(f"Failed to log member join to Discord: {str(e)}")

    @bot.event
    async def on_member_ban(guild: Guild, user: User):
        logger.info(f"Ban member {user.id}")

        db_user = users_database.get_user(user.id)
        if db_user is None:
            db_user = users_database.add_user(user.id)

        db_user.is_banned = True

        users_database.update_user(db_user)

        # Addition of logging embed
        log_channel = get_log_channel(guild)

        if log_channel is None:
            return
        try:
            async with create_interaction_embed_context(
                log_channel,
                user=None,
                description=f"{user.mention} was banned",
                timestamp=datetime.now(timezone.utc),
                footer="Member Banned",
            ) as embed:
                log_info_and_add_field(embed, logger, "Action", "/ban")
                log_info_and_add_field(embed, logger, "User", user.mention)
                log_info_and_add_field(
                    embed, logger, "Result", f"Successfully banned {user.mention}"
                )
        except Exception as e:
            logger.error(f"Failed to log ban event: {str(e)}")

    @bot.event
    async def on_member_unban(guild: Guild, user: User):
        logger.info(f"Unban member {user.id}")
        db_user = users_database.get_user(user.id)
        if db_user is None:
            db_user = users_database.add_user(user.id)

        db_user.is_banned = False

        users_database.update_user(db_user)

        # Addition of logging embed
        log_channel = get_log_channel(guild)

        if log_channel is None:
            return

        try:
            async with create_interaction_embed_context(
                log_channel,
                user=None,
                description=f"{user.mention} was unbanned",
                timestamp=datetime.now(timezone.utc),
                footer="Member Unbanned",
            ) as embed:
                log_info_and_add_field(embed, logger, "Action", "unban")
                log_info_and_add_field(embed, logger, "User", user.mention)
                log_info_and_add_field(
                    embed, logger, "Result", f"Successfully unbanned {user.mention}"
                )
        except Exception as e:
            logger.error(f"Failed to log unban event: {str(e)}")
