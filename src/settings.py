from pydantic import BaseModel
import os
import sys
import logging


class Settings(BaseModel):
    """Class for keeping track of settings"""

    guild_id: int
    discord_token: str = os.environ["DISCORD_TOKEN"]
    log_level: int = logging.INFO
    logging_channel_id: int
    postgres_host: str
    postgres_port: str
    database_name: str = "moddingway"
    postgres_username: str
    # TODO: investigate better secure password handling procedures
    postgres_password: str


def prod() -> Settings:
    return Settings(
        guild_id=1172230157776466050,
        logging_channel_id=1172324840947056681,
    )


def local() -> Settings:
    return Settings(
        guild_id=int(os.environ["GUILD_ID"]),
        logging_channel_id=int(os.environ["MOD_LOGGING_CHANNEL_ID"]),
        log_level=logging.DEBUG,
        postgres_host=os.environ.get("POSTGRES_HOST", "localhost"),
        postgres_port=os.environ.get("POSTGRES_PORT", "5432"),
        postgres_username=os.environ["POSTGRES_USER"],
        postgres_password=os.environ["POSTGRES_PASSWORD"],
    )


def get_settings() -> Settings:
    try:
        env_name = sys.argv[1].lower()
    except IndexError:
        env_name = "local"
    if env_name == "prod":
        return prod()
    else:
        return local()
