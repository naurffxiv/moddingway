from pydantic import BaseModel
import os
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
    postgres_username: str = os.environ["POSTGRES_USER"]
    postgres_password: str = os.environ["POSTGRES_PASSWORD"]
    automod_inactivity: dict[int, int]  # key: channel id, value: inactive limit (days)
    notify_channel_id: int


def prod() -> Settings:
    return Settings(
        guild_id=1172230157776466050,
        logging_channel_id=1172324840947056681,  # mod-reports
        notify_channel_id=1279952544235524269,  # bot-channel
        log_level=logging.INFO,
        postgres_host=os.environ.get("POSTGRES_HOST"),
        postgres_port=os.environ.get("POSTGRES_PORT"),
        automod_inactivity={
            1273263026744590468: 30,  # lfg
            1273261496968810598: 30,  # lfm
            1240356145311252615: 30,  # temporary
            1301166606985990144: 7,  # FRU
            1300527846468616302: 7,  # scheduled legacy
        },
    )


def local() -> Settings:
    inactive_forum_channel_id = os.environ.get("INACTIVE_FORUM_CHANNEL_ID")
    inactive_forum_duration = os.environ.get("INACTIVE_FORUM_DURATION")

    if inactive_forum_channel_id is not None and inactive_forum_duration is not None:
        automod_inactivity = {inactive_forum_channel_id: inactive_forum_duration}
    else:
        automod_inactivity = {}

    return Settings(
        guild_id=int(os.environ["GUILD_ID"]),
        logging_channel_id=int(os.environ["MOD_LOGGING_CHANNEL_ID"]),
        log_level=logging.DEBUG,
        postgres_host=os.environ.get("POSTGRES_HOST", "localhost"),
        postgres_port=os.environ.get("POSTGRES_PORT", "5432"),
        automod_inactivity=automod_inactivity,
        notify_channel_id=os.environ.get(
            "NOTIFY_CHANNEL_ID", os.environ["MOD_LOGGING_CHANNEL_ID"]
        ),
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
