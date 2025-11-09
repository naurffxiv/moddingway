import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import discord
from discord.utils import snowflake_time

from moddingway.settings import get_settings
from moddingway.util import (
    UnableToNotify,
    create_interaction_embed_context,
    get_log_channel,
)

settings = get_settings()
logger = logging.getLogger(__name__)


def create_autounexile_embed(
    self,
    user: Optional[discord.Member],
    discord_id: int,
    exile_id: str,
    end_timestamp: str,
):
    return create_interaction_embed_context(
        get_log_channel(self),
        user=user,
        timestamp=end_timestamp,
        description=f"<@{discord_id}>'s exile has timed out",
        footer=f"Exile ID: {exile_id}",
    )


def create_automod_embed(self, channel_id, num_removed, num_error, timestamp: datetime):
    return create_interaction_embed_context(
        get_log_channel(self),
        user=self.user,
        timestamp=timestamp,
        description=f"Successfully removed {num_removed} inactive thread(s) from <#{channel_id}>.\n{num_error} inactive thread(s) failed to be removed.",
    )


def create_channel_automod_embed(
    self, channel_id, num_removed, num_error, timestamp: datetime
):
    return create_interaction_embed_context(
        get_log_channel(self),
        user=self.user,
        timestamp=timestamp,
        description=f"Successfully removed {num_removed} old message(s) from <#{channel_id}>.\n{num_error} old messages(s) failed to be removed.",
    )


async def automod_thread(
    thread: discord.Thread,
    duration: int,
    num_removed: int,
    num_errors: int,
    user_id: Optional[int] = None,
):
    if thread.flags.pinned:
        # skip the for loop if the thread is pinned
        return num_removed, num_errors

    if user_id is not None and thread.owner.id != user_id:
        return num_removed, num_errors
    # check if starter message was deleted
    starter_message = None
    try:
        starter_message = await thread.fetch_message(thread.id)
        await asyncio.sleep(1)
    except discord.NotFound:
        pass
    except Exception as e:
        logger.error(e, exc_info=e)

    now = datetime.now(timezone.utc)
    last_post = thread.last_message_id
    time_since = now - snowflake_time(last_post)
    if starter_message is not None and time_since < timedelta(days=duration):
        return num_removed, num_errors

    # delete thread
    try:
        await thread.delete()
        logger.info(f"Thread {thread.id} has been deleted successfully")
        return num_removed + 1, num_errors
    except Exception as e:
        logger.error(f"Unexpected error for thread {thread.id}: {e}", exc_info=e)
        return num_removed, num_errors + 1


async def automod_channel(messages, duration: int, channel: str):
    num_removed = 0
    num_errors = 0

    async for message in messages:
        # Skip any pinned messages
        if message.pinned:
            continue

        # Delete message if older than 150 minutes
        now = datetime.now(timezone.utc)
        time_since = now - snowflake_time(message.id)
        if time_since > timedelta(minutes=duration):
            try:
                await message.delete()
                logger.info(
                    f"Message {message.id} has been deleted successfully from #{channel}"
                )
                num_removed += 1
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(
                    f"Unexpected error for message {message.id}: {e}", exc_info=e
                )
                num_errors += 1

    return num_removed, num_errors
