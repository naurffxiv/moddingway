import logging
from datetime import datetime, timezone

from discord.ext import tasks

from moddingway.settings import get_settings
from moddingway.util import create_interaction_embed_context, send_chunked_message

from .helper import automod_thread, create_automod_embed

settings = get_settings()
logger = logging.getLogger(__name__)


@tasks.loop(hours=24)
async def autodelete_threads(self):
    guild = self.get_guild(settings.guild_id)
    if guild is None:
        logger.error("Guild not found.")
        return

    notifying_channel = guild.get_channel(settings.notify_channel_id)
    if notifying_channel is None:
        logger.error("Notifying channel not found.")
        return

    for channel_id, duration in settings.automod_inactivity.items():
        num_removed = 0
        num_errors = 0
        try:
            channel = guild.get_channel(channel_id)
            if channel is None:
                logger.error("Forum channel not found.")
                continue

            async for thread in channel.archived_threads(limit=None):
                num_removed, num_errors = await automod_thread(
                    thread,
                    duration,
                    num_removed,
                    num_errors,
                )

            for thread in channel.threads:
                num_removed, num_errors = await automod_thread(
                    thread,
                    duration,
                    num_removed,
                    num_errors,
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
                logger.info(
                    f"No threads were marked for deletion in channel {channel_id}."
                )
        except Exception as e:
            logger.error(e)
            async with create_interaction_embed_context(
                self.get_channel(settings.logging_channel_id),
                user=self.user,
                timestamp=datetime.now(timezone.utc),
                description=f"Automod task failed to process channel <#{channel_id}>: {e}",
            ):
                pass
            continue
