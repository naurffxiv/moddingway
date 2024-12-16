import pytest
from pytest_mock.plugin import MockerFixture
from datetime import datetime
from typing import Optional
from moddingway import enums
from moddingway.database.models import User, Strike


@pytest.fixture
def create_role(mocker: MockerFixture):
    def __create_role(name: enums.Role):
        mocked_role = mocker.Mock()
        # name is used specifically in the Mock constructor
        # we need to configure it outside the constructor
        mocked_role.name = name.value

        return mocked_role

    return __create_role


@pytest.fixture
def naur_guild(mocker: MockerFixture, create_role):
    return mocker.Mock(
        roles=[
            create_role(enums.Role.MOD),
            create_role(enums.Role.VERIFIED),
            create_role(enums.Role.EXILED),
        ]
    )


@pytest.fixture
def create_db_user(mocker: MockerFixture):
    def __create_db_user(
        user_id: Optional[int] = None,
        discord_user_id: Optional[str] = None,
        discord_guild_id: Optional[str] = None,
        is_mod: Optional[bool] = None,
        temporary_points: Optional[int] = None,
        permanent_points: Optional[int] = None,
        last_infraction_timestamp: Optional[datetime] = None,
        get_strike_points: Optional[int] = None,
    ):
        mocked_user = mocker.Mock(spec=User)
        mocked_user.user_id = user_id
        mocked_user.discord_user_id = discord_user_id
        mocked_user.discord_guild_id = discord_guild_id
        mocked_user.is_mod = is_mod
        mocked_user.temporary_points = temporary_points
        mocked_user.permanent_points = permanent_points
        mocked_user.last_infraction_timestamp = last_infraction_timestamp
        mocked_user.get_strike_points = mocker.Mock(return_value=get_strike_points)
        return mocked_user

    return __create_db_user


# @pytest.fixture
# def create_db_strike(mocker: MockerFixture):
#     def __create_db_strike(
#         strike_id: Optional[int] = None,
#         user_id: Optional[int] = None,
#         severity: Optional[enums.StrikeSeverity] = None,
#         reason: Optional[str] = None,
#         created_timestamp: Optional[datetime] = None,
#         created_by: Optional[str] = None,
#         last_edited_timestamp: Optional[datetime] = None,
#         last_edited_by: Optional[str] = None,
#     ):
#         mocked_strike = mocker.Mock(spec=Strike)
#         mocked_strike.strike_id = strike_id
#         mocked_strike.user_id = user_id
#         mocked_strike.severity = severity
#         mocked_strike.reason = reason
#         mocked_strike.created_timestamp = created_timestamp
#         mocked_strike.created_by = created_by
#         mocked_strike.last_edited_timestamp = last_edited_timestamp
#         mocked_strike.last_edited_by = last_edited_by
#         return mocked_strike

#     return __create_db_strike
