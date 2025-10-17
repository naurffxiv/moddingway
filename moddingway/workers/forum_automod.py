import logging
from datetime import datetime, timezone

from discord.ext import tasks

from moddingway.settings import get_settings
from moddingway.util import (
    create_interaction_embed_context,
    send_chunked_message,
    get_log_channel,
    log_info_and_embed,
)

from .helper import (
    automod_thread,
    automod_channel,
    create_automod_embed,
    create_channel_automod_embed,
)

settings = get_settings()
logger = logging.getLogger(__name__)


# Worker for thread automodding
@tasks.loop(hours=24)
async def autodelete_threads(self):
    logger.info(f"Started forum automod worker task.")
    guild = self.get_guild(settings.guild_id)
    if guild is None:
        logger.error("Guild not found.")
        logger.info(f"Ended forum automod worker task with errors.")
        return

    notifying_channel = guild.get_channel(settings.notify_channel_id)
    if notifying_channel is None:
        logger.error("Notifying channel not found.")
        logger.info(f"Ended forum automod worker task with errors.")
        return

    for channel_id, duration in settings.automod_inactivity.items():
        num_removed = 0
        num_errors = 0
        user_id = None
        try:
            channel = guild.get_channel(channel_id)
            if channel is None:
                logger.error("Forum channel not found.")
                logger.info(f"Ended forum automod worker task with errors.")
                continue
            if channel_id == settings.event_forum_id:
                user_id = settings.event_bot_id
            async for thread in channel.archived_threads(limit=None):
                num_removed, num_errors = await automod_thread(
                    thread,
                    duration,
                    num_removed,
                    num_errors,
                    user_id,
                )

            for thread in channel.threads:
                num_removed, num_errors = await automod_thread(
                    thread,
                    duration,
                    num_removed,
                    num_errors,
                    user_id,
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
            logger.error(e, exc_info=e)
            async with create_interaction_embed_context(
                get_log_channel(self),
                user=self.user,
                timestamp=datetime.now(timezone.utc),
                description=f"Automod task failed to process channel <#{channel_id}>: {e}",
            ):
                pass
            continue
    logger.info(f"Completed forum automod worker task.")
    return f"Forum automod task completed."


# Worker for channel message automodding
@tasks.loop(hours=1)
async def autodelete_posts(self):
    logger.info(f"Started channel automod worker task.")
    guild = self.get_guild(settings.guild_id)
    if guild is None:
        logger.error("Guild not found.")
        logger.info(f"Ended channel automod worker task with errors.")
        return

    notifying_channel = guild.get_channel(settings.notify_channel_id)
    if notifying_channel is None:
        logger.error("Notifying channel not found.")
        logger.info(f"Ended channel automod worker task with errors.")
        return

    for channel_id, duration in settings.channel_automod_inactivity.items():

        try:
            channel = guild.get_channel(channel_id)
            if channel is None:
                logger.error("Message channel not found.")
                logger.info(f"Ended channel automod worker task with errors.")
                continue

            # Get channel messages
            messages = channel.history(limit=None)

            # Delete any messages longer than set duration
            num_removed, num_errors = await automod_channel(
                messages,
                duration,
            )

            # Log interally if any messages are removed or failed to be removed
            if num_removed > 0 or num_errors > 0:
                logger.info(
                    f"Removed a total of {num_removed} messages from channel {channel_id}. {num_errors} failed removals."
                )

                # Log externally to monitor channel if any messages are failed to be removed
                if num_errors > 0:
                    async with create_channel_automod_embed(
                        self,
                        channel_id,
                        num_removed,
                        num_errors,
                        datetime.now(timezone.utc),
                    ):
                        pass

            else:
                logger.info(
                    f"No messages were marked for deletion in channel {channel_id}."
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
    logger.info(f"Completed channel automod worker task.")
    return f"Channel automod task completed."


@autodelete_threads.before_loop
async def before_autodelete_threads():
    logger.info(f"Forum Automod started, task running every 24 hours.")
