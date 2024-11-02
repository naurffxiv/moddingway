from discord.ext import tasks
from discord.ext.commands import Bot
from database import exiles_database
from services.exile_service import unexile_user
from settings import get_settings
from .helper import create_autounexile_embed
import logging

settings = get_settings()
logger = logging.getLogger(__name__)


@tasks.loop(minutes=1.0)
async def autounexile_users(self):
    exiles = exiles_database.get_pending_unexiles()

    for exile in exiles:
        logger.info(f"Auto Unexile running on user id {exile.user_id}")
        try:
            error_message = None
            member = self.get_guild(settings.guild_id).get_member(exile.discord_id)

            async with create_autounexile_embed(
                self, member, exile.discord_id, exile.exile_id, exile.end_timestamp
            ) as autounexile_embed:
                if member is None:
                    error_message = f"<@{exile.discord_id}> was not found in the server"
                    logger.info(error_message)
                    raise Exception(error_message)

                error_message = await unexile_user(autounexile_embed, member)
            if error_message is not None:
                raise Exception(error_message)
        except Exception:
            logger.info(
                f"Auto Unexile failed, removing exile entry {exile.exile_id}: user {exile.discord_id}"
            )
            exiles_database.remove_user_exiles(exile.user_id)
