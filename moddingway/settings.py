import logging
import os
from .constants import AUTOMOD_INACTIVITY, STICKY_ROLES
from pydantic import BaseModel
from ast import literal_eval


class Settings(BaseModel):
    """Class for keeping track of settings"""

    guild_id: int
    discord_token: str = os.environ.get("DISCORD_TOKEN")
    log_level: int = logging.INFO
    logging_channel_id: int
    notify_channel_id: int
    postgres_host: str
    postgres_port: str
    database_name: str = "moddingway"
    postgres_username: str = os.environ.get("POSTGRES_USER")
    postgres_password: str = os.environ.get("POSTGRES_PASSWORD")
    automod_inactivity: dict[int, int]  # key: channel id, value: inactive limit (days)
    sticky_roles: list[
        int
    ]  # roles that grant access to channels that should be stripped/restored on exile/unexile


def prod() -> Settings:
    return Settings(
        guild_id=1172230157776466050,
        logging_channel_id=1172324840947056681,  # mod-reports
        notify_channel_id=1279952544235524269,  # bot-channel
        log_level=logging.INFO,
        postgres_host=os.environ.get("POSTGRES_HOST"),
        postgres_port=os.environ.get("POSTGRES_PORT"),
        automod_inactivity=AUTOMOD_INACTIVITY,
        sticky_roles=STICKY_ROLES,
    )


def local() -> Settings:
    inactive_forum_channel_id = os.environ.get("INACTIVE_FORUM_CHANNEL_ID")
    inactive_forum_duration = os.environ.get("INACTIVE_FORUM_DURATION")

    if inactive_forum_channel_id is not None and inactive_forum_duration is not None:
        automod_inactivity = {inactive_forum_channel_id: inactive_forum_duration}
    else:
        automod_inactivity = {}

    return Settings(
        guild_id=int(os.environ.get("GUILD_ID", 0)),
        logging_channel_id=int(os.environ.get("MOD_LOGGING_CHANNEL_ID", 0)),
        log_level=logging.DEBUG,
        postgres_host=os.environ.get("POSTGRES_HOST", "localhost"),
        postgres_port=os.environ.get(
            "POSTGRES_PORT", "5433"
        ),  # Define Port as 5432 for persistent data mode, or 5433 for ephemeral
        automod_inactivity=automod_inactivity,
        notify_channel_id=os.environ.get(
            "NOTIFY_CHANNEL_ID", os.environ.get("MOD_LOGGING_CHANNEL_ID", 0)
        ),
        sticky_roles=literal_eval(os.environ.get("STICKY_ROLE_ARRAY", "None")) or [],
    )


def get_settings() -> Settings:
    try:
        env_name = os.environ["MODDINGWAY_ENVIRONMENT"].lower()
    except KeyError:
        env_name = "local"
    if env_name == "prod":
        return prod()
    else:
        return local()
