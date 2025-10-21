import logging
from datetime import datetime, timezone
import discord
import asyncio, re

from discord import Guild, User, Thread
from discord.ext.commands import Bot

from moddingway.database import users_database
from moddingway.constants import Role
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
                log_info_and_add_field(embed, logger, "Action", "/unban")
                log_info_and_add_field(embed, logger, "User", user.mention)
                log_info_and_add_field(
                    embed, logger, "Result", f"Successfully unbanned {user.mention}"
                )
        except Exception as e:
            logger.error(f"Failed to log unban event: {str(e)}")

    @bot.event
    async def on_thread_create(thread: Thread):
        # Handle new threads created in the event forum by raid-helper.
        INITIAL_DELAY = 0.5
        WARNING_THRESHOLD = 86400  # 24 hours

        # Only process threads from raid-helper in the event forum
        if (
            thread.parent_id != settings.event_forum_id
            or thread.owner_id != settings.event_bot_id
        ):
            return

        try:
            # Raidhelper bot sends a dummy message first then edits later so we are using sleep to get edited version because on_message_edit event listens for all message edits in the server
            await asyncio.sleep(INITIAL_DELAY)

            # Fetch the thread's initial message
            try:
                message = await thread.fetch_message(thread.id)
            except Exception as e:
                logger.error(f"Failed to fetch message in event thread f{thread.id}")

            if not message or not message.content:
                logger.error(f"No message content found in event thread {thread.id}")
                return
            # Extract timestamp from Discord's timestamp format
            date_pattern = re.compile(r"<t:(\d+):F>")
            date_match = date_pattern.search(message.content)

            if not date_match:
                logger.error(f"No timestamp found in thread {thread.id}")
                return

            timestamp = int(date_match.group(1))
            current_timestamp = int(datetime.now().timestamp())
            time_difference = timestamp - current_timestamp

            # Extract leader username
            user_pattern = re.compile(r"<@[0-9]+>")
            user_match = user_pattern.search(message.content)

            if user_match and time_difference <= WARNING_THRESHOLD:
                try:
                    warn_channel = await bot.fetch_channel(
                        settings.event_warn_channel_id
                    )
                    await warn_channel.send(
                        content=f"{user_match.group(0)} Warning: The event you have scheduled starts in less than 24 hours!"
                    )
                    logger.info(
                        f"Sent warning for thread {thread.id} (starts in {time_difference}s)"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to send warning message in event channel {warn_channel.id}"
                    )
            else:
                hours = time_difference // 3600
                logger.info(f"Event in thread {thread.id} starts in {hours} hours")

        except Exception as e:
            logger.error(
                f"Unexpected error processing event thread {thread.id}: {e}",
                exc_info=True,
            )
