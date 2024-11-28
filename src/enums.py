from enum import StrEnum, IntEnum


class Role(StrEnum):
    EXILED = "Exiled"
    VERIFIED = "Verified"
    MOD = "Mod"
    ADMING = "Admin"


class ExileStatus(IntEnum):
    TIMED_EXILED = 1
    UNEXILED = 2
    UNKNOWN = 3


class StrikeSeverity(IntEnum):
    MINOR = 1
    MODERATE = 2
    SERIOUS = 3
