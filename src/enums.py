from enum import StrEnum, IntEnum


class Role(StrEnum):
    EXILED = "Exiled"
    VERIFIED = "Verified"
    ADMINISTRATION = "Administration"
    MANAGEMENT = "Management"


class ExileStatus(IntEnum):
    INDEFINITE_EXILE = 0
    TIMED_EXILED = 1
    UNEXILED = 2
