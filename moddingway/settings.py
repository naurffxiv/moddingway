import logging
import os
from .constants import AUTOMOD_INACTIVITY, CHANNEL_AUTOMOD_INACTIVITY, STICKY_ROLES
from pydantic import BaseModel
from ast import literal_eval


logger = logging.getLogger(__name__)


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
    channel_automod_inactivity: dict[
        int, int
    ]  # key: channel id, value: inactive limit (minutes)
    event_bot_id: int
    event_forum_id: int
    event_warn_channel_id: int
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
        channel_automod_inactivity=CHANNEL_AUTOMOD_INACTIVITY,
        event_bot_id=579155972115660803,  # Raid-Helper#3806
        event_forum_id=1419357090841104544,  # PtC event forum
        event_warn_channel_id=1426273165491048538,  # event warn channel
        sticky_roles=STICKY_ROLES,
    )


def local() -> Settings:
    automod_inactivity = {}
    channel_automod_inactivity = {}

    inactive_forum_channel_id = os.environ.get("INACTIVE_FORUM_CHANNEL_ID", "")
    inactive_forum_duration = os.environ.get("INACTIVE_FORUM_DURATION", "")
    if inactive_forum_channel_id != "" and inactive_forum_duration != "":
        automod_inactivity[int(inactive_forum_channel_id)] = int(
            inactive_forum_duration
        )

    inactive_event_forum_channel_id = os.environ.get("PTC_EVENT_FORUM_ID", "")
    inactive_event_forum_duration = os.environ.get("PTC_EVENT_FORUM_DURATION", "")
    if inactive_event_forum_channel_id != "" and inactive_event_forum_duration != "":
        automod_inactivity[int(inactive_event_forum_channel_id)] = int(
            inactive_event_forum_duration
        )

    pf_recruitment_channel_id = os.environ.get("PF_RECRUITMENT_CHANNEL_ID", "")
    pf_recruitment_channel_duration = os.environ.get(
        "PF_RECRUITMENT_CHANNEL_DURATION", ""
    )
    if pf_recruitment_channel_id != "":
        channel_automod_inactivity[int(pf_recruitment_channel_id)] = int(
            pf_recruitment_channel_duration
        )

    notify_channel_id = os.environ.get("NOTIFY_CHANNEL_ID", "")
    if notify_channel_id == "":
        notify_channel_id = os.environ.get("MOD_LOGGING_CHANNEL_ID", 0)

    return Settings(
        guild_id=int(os.environ.get("GUILD_ID", 0)),
        logging_channel_id=int(os.environ.get("MOD_LOGGING_CHANNEL_ID", 0)),
        log_level=logging.DEBUG,
        postgres_host=os.environ.get("POSTGRES_HOST", "localhost"),
        postgres_port=os.environ.get("POSTGRES_PORT", "5432"),
        automod_inactivity=automod_inactivity,
        channel_automod_inactivity=channel_automod_inactivity,
        event_bot_id=_check_env_convert("EVENT_BOT_ID"),
        event_forum_id=_check_env_convert("PTC_EVENT_FORUM_ID"),
        event_warn_channel_id=_check_env_convert("EVENT_WARN_CHANNEL"),
        notify_channel_id=notify_channel_id,
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


def _check_env_convert(key: str, default: int = 0) -> int:
    value_str = os.environ.get(key)

    if value_str is None or value_str == "":
        return default

    try:
        return int(value_str)
    except ValueError:
        logger.info(f"ENV {key} is not set to {value_str}, returning {default}.")
