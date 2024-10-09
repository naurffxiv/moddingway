import discord
from bot import ModdingwayBot
from settings import get_settings
import logging
from database import DatabaseConnection

settings = get_settings()

# TODO:
# dockerize
# error handling at the app level


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=settings.log_level)

    intents = discord.Intents.default()
    bot = ModdingwayBot(command_prefix="/", intents=intents)

    database_connection = DatabaseConnection()
    database_connection.connect()
    database_connection.create_tables()

    bot.run(settings.discord_token)
