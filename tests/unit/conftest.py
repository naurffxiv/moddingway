import datetime
from typing import List

import pytest
from pytest_mock.plugin import MockerFixture

from moddingway import enums

DEFAULT_DATETIME_NOW = datetime.datetime(
    2019, 11, 19, 8, 0, 0, tzinfo=datetime.timezone.utc
)


@pytest.fixture(autouse=True)
def mock_datetime_now(mocker: MockerFixture, monkeypatch):
    datetime_mock = mocker.MagicMock(wraps=datetime.datetime)
    datetime_mock.now.return_value = DEFAULT_DATETIME_NOW
    monkeypatch.setattr(datetime, "datetime", datetime_mock)


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
def create_member(mocker: MockerFixture, naur_guild, create_role):
    def __create_member(
        roles: List[enums.Role] = [enums.Role.VERIFIED], allows_dms: bool = True
    ):
        role_list = [create_role(role) for role in roles]
        mocked_member = mocker.Mock(
            guild=naur_guild,
            roles=role_list,
            add_roles=mocker.AsyncMock(),
            remove_roles=mocker.AsyncMock(),
        )

        mocked_member.create_dm = mocker.AsyncMock()
        if not allows_dms:
            mocked_member.create_dm.side_effect = Exception("Cannot create DM")

        return mocked_member

    return __create_member
