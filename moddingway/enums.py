from enum import IntEnum, StrEnum


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
