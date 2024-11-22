import discord
import logging
from enums import StrikeSeverity
from database import users_database
from database.models import create_empty_user
from util import log_info_and_embed

logger = logging.getLogger(__name__)


async def add_strike(
    logging_embed: discord.Embed,
    user: discord.Member,
    severity: StrikeSeverity,
    reason: str,
):
    # find user in DB
    db_user = users_database.get_user(user.id)
    if db_user is None:
        log_info_and_embed(
            logging_embed,
            logger,
            f"User not found in database, creating new record",
        )
        db_user_id = users_database.add_user(user.id)
        logger.info(f"Created user record in DB with id {db_user_id}")

        db_user = create_empty_user(db_user_id, user.id, None, None)

    # create strike

    # increment user points, update

    # apply punishments
