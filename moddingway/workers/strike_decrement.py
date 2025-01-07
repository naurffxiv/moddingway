import logging

from discord.ext import tasks

from moddingway.database import users_database

logger = logging.getLogger(__name__)


@tasks.loop(hours=24)
async def decrement_strikes(self):
    try:
        row_count = users_database.decrement_old_strike_points()
        logger.info(f"Finished decrementing old strikes, updated {row_count} users")
    except Exception as e:
        logger.error("Error when decrementing old user strikes", exc_info=e)
