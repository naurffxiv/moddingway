from datetime import datetime, timezone, timedelta
import logging
import asyncio
import discord
from discord.utils import snowflake_time
from discord.ext.commands import Bot
from settings import get_settings
from util import create_interaction_embed_context, send_dm, UnableToDM
from typing import Optional


settings = get_settings()
logger = logging.getLogger(__name__)


def create_autounexile_embed(
    self, user: discord.User, exile_id: str, end_timestamp: str
):
    return create_interaction_embed_context(
        self.get_channel(settings.logging_channel_id),
        user=user,
        timestamp=end_timestamp,
        description=f"<@{user.id}>'s exile has timed out",
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
):
    if thread.flags.pinned:
        # skip the for loop if the thread is pinned
        return num_removed, num_errors

    # check if starter message was deleted
    starter_message = None
    try:
        starter_message = await thread.fetch_message(thread.id)
        await asyncio.sleep(0.5)
    except discord.NotFound:
        pass
    except Exception as e:
        logger.error(e)

    now = datetime.now(timezone.utc)
    last_post = thread.last_message_id
    time_since = now - snowflake_time(last_post)
    if starter_message is not None and time_since < timedelta(days=duration):
        return num_removed, num_errors

    # delete thread and try to send DM to user
    try:
        await thread.delete()
        logger.info(f"Thread {thread.id} has been deleted successfully")
        ret = num_removed + 1, num_errors
        # TODO: uncomment DM portion and sleep when backlog is dealt with
        # if thread.owner is not None:
        #     try:
        #         await send_dm(
        #             thread.owner,
        #             f'Your thread "{thread.name}" in <#{channel_id}> has been automatically deleted as {duration} days have passed without any activity or the starter message has been deleted.',
        #         )
        #     except discord.Forbidden:
        #         raise UnableToDM("User has DMs disabled")
        # else:
        #     raise UnableToDM("User is not in the server")
        return ret
    except UnableToDM as e:
        logger.info(f"Unable to DM user {thread.owner_id}: {e}")
        channel = self.get_channel(settings.logging_channel_id)
        async with create_interaction_embed_context(
            channel,
            user=thread.owner,
            timestamp=datetime.now(timezone.utc),
            description=f"<@{thread.owner_id}>'s thread was deleted in <#{channel_id}> but a DM could not be sent: {e}",
        ):
            pass
    except Exception as e:
        logger.error(e)
        return num_removed, num_errors + 1
    # await asyncio.sleep(300)
