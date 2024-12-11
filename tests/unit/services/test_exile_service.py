from pytest_mock.plugin import MockerFixture

from moddingway.database.models import User
from moddingway.services import exile_service
from datetime import timedelta
from moddingway import enums


async def test_exile_user__unverified(mocker: MockerFixture, create_member):
    # Arrange
    mocked_member = create_member(roles=[enums.Role.EXILED])

    # Act
    res = await exile_service.exile_user(
        mocker.Mock(), mocked_member, timedelta(days=1), "test_exile_user__unverified"
    )

    # Assert
    assert res is not None
    assert res == "User is not currently verified, no action will be taken"


async def test_exile_user__verified_existing_user_dm_failed(mocker: MockerFixture, create_member):
    # Arrange
    mock_database_user = User(
        user_id=1,
        discord_user_id="12345",
        discord_guild_id="1",
        is_mod=False,
        temporary_points=0,
        permanent_points=0,
    )
    mocker.patch("moddingway.database.users_database.get_user", return_value=mock_database_user)
    mocker.patch("moddingway.database.exiles_database.add_exile", return_value=4001)

    mocked_member = create_member(roles=[enums.Role.VERIFIED])

    # Act
    res = await exile_service.exile_user(
        mocker.Mock(),
        mocked_member,
        timedelta(days=1),
        "test_exile_user verified existing_user dm_failed",
    )

    # Assert
    assert res is None
