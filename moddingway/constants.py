from enum import IntEnum, StrEnum


# Class Constants
class Role(StrEnum):
    EXILED = "Exiled"
    NON_VERIFIED = "Non-Verified"
    VERIFIED = "Verified"
    MOD = "Mod"


class ExileStatus(IntEnum):
    TIMED_EXILED = 1
    UNEXILED = 2
    UNKNOWN = 3


class StrikeSeverity(IntEnum):
    MINOR = 1
    MODERATE = 2
    SERIOUS = 3


class UserRole(IntEnum):
    SYSADMIN = 3
    MOD = 2
    USER = 1


# Strikes constants
MINOR_INFRACTION_POINTS = 1
MODERATE_INFRACTION_POINTS = 3
SERIOUS_INFRACTION_POINTS = 7

# Strikes threshold and punisment array
THRESHOLDS_PUNISHMENT = [
    # Point threshold and punishment amount
    (10, 14),
    (7, 7),
    (5, 3),
    (3, 1),
]

AUTOMOD_INACTIVITY = {
    1273263026744590468: 30,  # lfg
    1273261496968810598: 30,  # lfm
    1240356145311252615: 30,  # temporary
    1301166606985990144: 14,  # scheduled pfs
    1419357090841104544: 3,  # PtC event forum
}

STICKY_ROLES = [
    # Extra roles that should be removed from users when they are exiled
    1253810157524094996,  # Glorp
    1272364706241187870,  # Event Ping
]

# Central location for custom Error Messages for better mod readability
ERROR_MESSAGES = {
    # Error Messages should have <@{user}> and {context} variables
    # <@{user}> displays the user effected
    # {context} gives context to where the error originated
    50007: "Failed to send DM to <@{user}> for {context}: user has DMs disabled or blocked the bot (error code: 50007).",
}