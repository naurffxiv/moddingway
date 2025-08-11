import logging
from datetime import datetime, timezone

from discord.ext import tasks

from moddingway.settings import get_settings
from moddingway.util import (
    create_interaction_embed_context,
    send_chunked_message,
    get_log_channel,
)

from .helper import automod_thread, create_automod_embed

settings = get_settings()
logger = logging.getLogger(__name__)


@tasks.loop(hours=24)
async def autodelete_threads(self):
    logger.info(f"[automod] Started forum automod worker task - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")

    guild = self.get_guild(settings.guild_id)
    if guild is None:
        logger.error("[automod] Guild not found.")
        logger.info(
            f"[automod] Ended forum automod worker task with errors - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
        return

    notifying_channel = guild.get_channel(settings.notify_channel_id)
    if notifying_channel is None:
        logger.error("[automod] Notifying channel not found.")
        logger.info(
            f"[automod] Ended forum automod worker task with errors - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
        return

    for channel_id, duration in settings.automod_inactivity.items():
        num_removed = 0
        num_errors = 0
        try:
            channel = guild.get_channel(channel_id)
            if channel is None:
                logger.error("[automod] Forum channel not found.")
                logger.info(
                    f"[automod] Ended forum automod worker task with errors - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
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
                    f"[automod] Removed a total of {num_removed} threads from channel {channel_id}. {num_errors} failed removals."
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
                    f"[automod] No threads were marked for deletion in channel {channel_id}."
                )
        except Exception as e:
            logger.error(e, exc_info=e)
            async with create_interaction_embed_context(
                get_log_channel(self),
                user=self.user,
                timestamp=datetime.now(timezone.utc),
                description=f"Automod task failed to process channel <#{channel_id}>: {e}",
            ):
                pass
            continue

    logger.info(f"[automod] Completed forum automod worker task - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")


@autodelete_threads.before_loop
async def before_autodelete_threads():
    logger.info(f"[automod] forum automod worker started,"
                f" task running every 24 hours - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
