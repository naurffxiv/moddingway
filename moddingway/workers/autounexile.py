import logging

from discord.ext import tasks
from datetime import datetime

from moddingway.database import exiles_database
from moddingway.constants import ExileStatus
from moddingway.services.exile_service import unexile_user
from moddingway.settings import get_settings

from .helper import create_autounexile_embed

settings = get_settings()
logger = logging.getLogger(__name__)


@tasks.loop(minutes=1.0)
async def autounexile_users(self):
    try:
        exiles = exiles_database.get_pending_unexiles()
    except Exception:
        logger.info("[unexile] Failed to get pending exiles.")
        logger.info(f"[unexile] Ended auto unexile worker task with errors "
                    f"- {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
        return

    for exile in exiles:
        logger.info(f"[unexile] Auto Unexile running on user id {exile.user_id}")
        try:
            error_message = None
            member = self.get_guild(settings.guild_id).get_member(exile.discord_id)

            async with create_autounexile_embed(
                    self, member, exile.discord_id, exile.exile_id, exile.end_timestamp
            ) as autounexile_embed:
                if member is None:
                    error_message = f"<@{exile.discord_id}> was not found in the server"
                    logger.error(f"[unexile] {error_message}")
                    raise Exception(error_message)

                error_message = await unexile_user(autounexile_embed, member)
            if error_message is not None:
                raise Exception(error_message)
        except Exception:
            logger.info(
                f"[unxile] Auto Unexile failed, updating exile status of exile "
                f"{exile.exile_id}, user {exile.discord_id} to unknown"
            )
            logger.info(f"[unexile] Ended auto unexile worker task with errors "
                        f"- {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
            exiles_database.update_exile_status(exile.exile_id, ExileStatus.UNKNOWN)


@autounexile_users.before_loop
async def before_autounexile_users():
    logger.info(f"[unexile] auto unexile worker started,"
                f" task running every 1 minute - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
