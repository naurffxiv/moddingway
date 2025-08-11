import logging

from datetime import datetime

from discord.ext import tasks

from moddingway.database import users_database

logger = logging.getLogger(__name__)


@tasks.loop(hours=24)
async def decrement_strikes(self):
    try:
        row_count = users_database.decrement_old_strike_points()
        logger.info(
            f"[strike decrement] Finished decrementing old strikes, updated {row_count} users"
        )
    except Exception as e:
        logger.error(
            "[strike decrement] Error when decrementing old user strikes", exc_info=e
        )


@decrement_strikes.before_loop
async def before_decrement_strikes():
    logger.info(
        f"[strike decrement] strike decrement worker started,"
        f" task running every 24 hours - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
    )
