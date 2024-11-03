from datetime import datetime, timezone, timedelta
import discord
import logging
import asyncio
from settings import get_settings
from util import send_dm, create_interaction_embed_context
from .helper import create_automod_embed
from discord.ext import tasks
from discord.utils import snowflake_time

settings = get_settings()
logger = logging.getLogger(__name__)


class UnableToDM(Exception):
    pass


@tasks.loop(hours=24)
async def autodelete_threads(self):
    guild = self.get_guild(settings.guild_id)
    if guild is None:
        logger.error("Guild not found.")
        return

    for channel_id, duration in settings.automod_inactivity.items():
        num_removed = 0
        num_error = 0
        channel = guild.get_channel(channel_id)
        if channel is None:
            continue

        for thread in channel.threads:
            if thread.flags.pinned:
                # skip the for loop if the thread is pinned
                continue

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
                continue

            # delete thread and try to send DM to user
            try:
                await thread.delete()
                logger.info(f"Thread {thread.id} has been deleted successfully")
                num_removed += 1

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
                num_error += 1
            # await asyncio.sleep(300)
        async with create_automod_embed(
            self, channel_id, num_removed, num_error, datetime.now(timezone.utc)
        ):
            pass
