from datetime import datetime, timezone, timedelta
import discord
import logging
import asyncio
from settings import get_settings
from util import log_info_and_embed, send_dm
from .helper import create_automod_embed
from discord.ext import tasks
from discord.utils import snowflake_time

settings = get_settings()
logger = logging.getLogger(__name__)


@tasks.loop(hours=24)
async def autodelete_threads(self):
    guild = self.get_guild(settings.guild_id)
    if guild is None:
        logger.error("Guild not found.")
        return

    for channel_id, duration in settings.automod_inactivity.items():
        channel = guild.get_channel(channel_id)
        if channel is None:
            continue

        for thread in channel.threads:
            # skip the for loop if the thread is pinned
            if thread.flags.pinned:
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
                async with create_automod_embed(
                    self,
                    thread,
                    now,
                ) as automod_embed:
                    await thread.delete()
                    log_info_and_embed(
                        automod_embed, logger, "Thread has been deleted successfully."
                    )

                    # TODO: uncomment DM portion and sleep when backlog is dealt with
                    # if thread.owner is not None:
                    #     await send_dm(
                    #         thread.owner,
                    #         f'Your thread "{thread.name}" in <#{channel_id}> has been automatically deleted as {duration} days have passed without any activity or the starter message has been deleted.',
                    #     )
                    # else:
                    #     log_info_and_embed(automod_embed, logger, "Unable to DM user.")
            except Exception as e:
                logger.error(e)
            # await asyncio.sleep(300)
