import logging

import discord

from moddingway.bot import ModdingwayBot
from moddingway.database import DatabaseConnection
from moddingway.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()])

    intents = discord.Intents.default()
    intents.members = True
    bot = ModdingwayBot(command_prefix="/", intents=intents)

    database_connection = DatabaseConnection()
    database_connection.connect()
    database_connection.create_tables()

    bot.run(settings.discord_token)
