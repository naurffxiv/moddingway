import discord
from moddingway.bot import ModdingwayBot
from moddingway.settings import get_settings
import logging
from moddingway.database import DatabaseConnection

settings = get_settings()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=settings.log_level)

    intents = discord.Intents.default()
    intents.members = True
    bot = ModdingwayBot(command_prefix="/", intents=intents)

    database_connection = DatabaseConnection()
    database_connection.connect()
    database_connection.create_tables()

    bot.run(settings.discord_token)
