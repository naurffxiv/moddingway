from enum import StrEnum, IntEnum


class Role(StrEnum):
    EXILED = "Exiled"
    VERIFIED = "Verified"
    ADMINISTRATION = "Administration"
    MANAGEMENT = "Management"
    MOD = "Mod"


class ExileStatus(IntEnum):
    TIMED_EXILED = 1
    UNEXILED = 2
    UNKNOWN = 3
