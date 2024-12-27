import datetime
from typing import List
import pytest
from pytest_mock.plugin import MockerFixture

# from datetime import datetime
from typing import Optional
from moddingway import enums
from moddingway.database.models import User, Strike
import discord

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
        roles: List[enums.Role] = [enums.Role.VERIFIED],
        allows_dms: bool = True,
        id: Optional[int] = None,
    ):
        role_list = [create_role(role) for role in roles]
        mocked_member = mocker.Mock(
            spec=discord.member,
            guild=naur_guild,
            roles=role_list,
            id=id,
            add_roles=mocker.AsyncMock(),
            remove_roles=mocker.AsyncMock(),
        )

        mocked_member.create_dm = mocker.AsyncMock()
        if not allows_dms:
            mocked_member.create_dm.side_effect = Exception("Cannot create DM")

        return mocked_member

    return __create_member


@pytest.fixture
def create_db_user(mocker: MockerFixture):
    def __create_db_user(
        user_id: Optional[int] = None,
        discord_user_id: Optional[str] = None,
        discord_guild_id: Optional[str] = None,
        is_mod: Optional[bool] = None,
        temporary_points: Optional[int] = None,
        permanent_points: Optional[int] = None,
        last_infraction_timestamp: Optional[datetime.datetime] = None,
        get_strike_points: Optional[int] = None,
    ):
        mocked_user = mocker.Mock(
            spec=User,
            user_id=user_id,
            discord_user_id=discord_user_id,
            discord_guild_id=discord_guild_id,
            is_mod=is_mod,
            temporary_points=temporary_points,
            permanent_points=permanent_points,
            last_infraction_timestamp=last_infraction_timestamp,
            get_strike_points=mocker.Mock(return_value=get_strike_points),
        )
        return mocked_user

    return __create_db_user


@pytest.fixture
def create_embed(mocker: MockerFixture):
    def __create_embed():
        mocked_user = mocker.Mock(spec=discord.Embed)
        return mocked_user

    return __create_embed
