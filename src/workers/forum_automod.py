from datetime import datetime, timezone, timedelta
import discord
import logging
import asyncio
from settings import get_settings
from util import send_dm, create_interaction_embed_context
from .helper import create_automod_embed, automod_thread
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
        num_removed = 0
        num_errors = 0
        channel = guild.get_channel(channel_id)
        if channel is None:
            continue

        async for thread in channel.archived_threads(limit=None):
            num_removed, num_errors = await automod_thread(
                self, channel_id, thread, duration, num_removed, num_errors
            )

        for thread in channel.threads:
            num_removed, num_errors = await automod_thread(
                self, channel_id, thread, duration, num_removed, num_errors
            )

        if num_removed > 0 or num_errors > 0:
            logger.info(
                f"Removed a total of {num_removed} threads from channel {channel_id}. {num_errors} failed removals."
            )
            async with create_automod_embed(
                self,
                channel_id,
                num_removed,
                num_errors,
                datetime.now(timezone.utc),
            ):
                pass
        else:
            logger.info(f"No threads were marked for deletion in channel {channel_id}.")
