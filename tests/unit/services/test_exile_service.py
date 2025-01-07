from pytest_mock.plugin import MockerFixture
from moddingway.database.models import User
from moddingway.services import exile_service
from datetime import timedelta
from moddingway import enums
import pytest


@pytest.mark.asyncio
async def test_exile_user__unverified(mocker: MockerFixture, create_member):
    # Arrange
    mocked_member = create_member()
    mock_database_user = User(
        user_id=1,
        discord_user_id="12345",
        discord_guild_id="1",
        is_mod=False,
        temporary_points=0,
        permanent_points=0,
    )
    mocker.patch(
        "moddingway.database.users_database.get_user", return_value=mock_database_user
    )
    mocker.patch(
        "moddingway.database.exiles_database.get_user_active_exile", return_value=None
    )
    mocker.patch("moddingway.util.user_has_role", return_value=False)
    # Act
    res = await exile_service.exile_user(
        mocker.Mock(description=""),
        mocked_member,
        timedelta(days=1),
        "test_exile_user__unverified",
    )

    # Assert
    assert res is not None
    assert res == "User is not currently verified, no action will be taken"


@pytest.mark.asyncio
async def test_exile_user__verified_existing_user_dm_failed(
    mocker: MockerFixture, create_member
):
    # Arrange
    mock_database_user = User(
        user_id=1,
        discord_user_id="12345",
        discord_guild_id="1",
        is_mod=False,
        temporary_points=0,
        permanent_points=0,
    )
    mocker.patch(
        "moddingway.database.exiles_database.get_user_active_exile", return_value=None
    )
    mocker.patch(
        "moddingway.database.users_database.get_user", return_value=mock_database_user
    )
    create_user_mock = mocker.patch(
        "moddingway.database.users_database.add_user", return_value=mock_database_user
    )
    exile_id = 4001
    mocker.patch("moddingway.database.exiles_database.add_exile", return_value=exile_id)

    mocked_member = create_member(roles=[enums.Role.VERIFIED], allows_dms=False)
    mocked_logging_embed = mocker.Mock()

    # Act
    res = await exile_service.exile_user(
        mocked_logging_embed,
        mocked_member,
        timedelta(days=1),
        "test_exile_user verified existing_user dm_failed",
    )

    # Assert
    assert res is None
    create_user_mock.assert_not_called()
    mocked_logging_embed.set_footer.assert_called_with(text=f"Exile ID: {exile_id}")
    # TODO check exile create call to confirm data is correct

    assert any(
        call[1].get("name", "") == "DM Status"
        for call in mocked_logging_embed.add_field.call_args_list
    )
