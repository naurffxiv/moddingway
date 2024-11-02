from discord.ext import tasks
from discord.ext.commands import Bot
from database import exiles_database
from services.exile_service import unexile_user
from settings import get_settings
from .helper import create_autounexile_embed
import logging

settings = get_settings()
logger = logging.getLogger(__name__)


# @tasks.loop(minutes=1.0)
async def autounexile_users(self):
    exiles = exiles_database.get_pending_unexiles()

    for exile in exiles:
        logger.info(f"Auto Unexile running on user id {exile.user_id}")
        member = self.get_guild(settings.guild_id).get_member(exile.user_id)
        if member is not None:
            async with create_autounexile_embed(
                self, member, exile.exile_id, exile.end_timestamp
            ) as autounexile_embed:
                await unexile_user(autounexile_embed, member)
        else:
            logger.error(f"User {exile.user_id} not found in server")

        exiles_database.remove_user_exiles(
            exile.user_id
        )  # remove entry from database no matter what
