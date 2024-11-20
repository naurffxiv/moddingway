from datetime import datetime, timezone, timedelta
import logging
import asyncio
import discord
from discord.utils import snowflake_time
from discord.ext.commands import Bot
from settings import get_settings
from util import create_interaction_embed_context, send_dm, UnableToNotify
from typing import Optional


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
        self.get_channel(settings.logging_channel_id),
        user=user,
        timestamp=end_timestamp,
        description=f"<@{discord_id}>'s exile has timed out",
        footer=f"Exile ID: {exile_id}",
    )


def create_automod_embed(self, channel_id, num_removed, num_error, timestamp: datetime):
    return create_interaction_embed_context(
        self.get_channel(settings.logging_channel_id),
        user=self.user,
        timestamp=timestamp,
        description=f"Successfully removed {num_removed} inactive thread(s) from <#{channel_id}>.\n{num_error} inactive thread(s) failed to be removed.",
    )


async def automod_thread(
    self,
    channel_id,
    thread: discord.Thread,
    duration: int,
    num_removed: int,
    num_errors: int,
    user_list: list[int],
):
    if thread.flags.pinned:
        # skip the for loop if the thread is pinned
        return num_removed, num_errors

    # check if starter message was deleted
    starter_message = None
    try:
        starter_message = await thread.fetch_message(thread.id)
        await asyncio.sleep(1)
    except discord.NotFound:
        pass
    except Exception as e:
        logger.error(e)

    now = datetime.now(timezone.utc)
    last_post = thread.last_message_id
    time_since = now - snowflake_time(last_post)
    if starter_message is not None and time_since < timedelta(days=duration):
        return num_removed, num_errors

    # delete thread and try to notify to user
    try:
        await thread.delete()
        logger.info(f"Thread {thread.id} has been deleted successfully")
        ret = num_removed + 1, num_errors
        if thread.owner is not None:
            if thread.owner_id not in user_list:
                user_list.append(thread.owner_id)
        else:
            raise UnableToNotify("User is not in the server")
        return ret
    except UnableToNotify as e:
        logger.info(f"Unable to notify user {thread.owner_id}: {e}")
        channel = self.get_channel(settings.logging_channel_id)
        async with create_interaction_embed_context(
            channel,
            user=thread.owner,
            timestamp=datetime.now(timezone.utc),
            description=f"<@{thread.owner_id}>'s thread was deleted in <#{channel_id}> but a notification could not be sent: {e}",
        ):
            pass
        # NB: not really an error we're worried about since it's just notifying
        return num_removed + 1, num_errors
    except Exception as e:
        logger.error(f"Unexpected error for thread {thread.id}: {e}")
        return num_removed, num_errors + 1
