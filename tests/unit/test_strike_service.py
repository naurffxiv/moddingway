import pytest
from pytest_mock.plugin import MockerFixture
from moddingway.database.models import Strike
from moddingway.services import strike_service
from moddingway import enums
from typing import List
import discord


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "previous_points,total_points,expected_punishment",
    [
        (0, 1, "Nothing"),
        (1, 8, "11 day exile"),
        (8, 10, "14 day exile"),
        (10, 11, "14 day exile"),
        (1, 9, "11 day exile"),
        (9, 12, "14 day exile"),
        (12, 13, "14 day exile"),
        (10, 15, "Permanent ban"),
    ],
)
async def test_apply_punisment(
    previous_points: int,
    total_points: int,
    expected_punishment: str,
    mocker: MockerFixture,
    create_db_user,
):
    mocked_logging_embed = mocker.Mock()
    mocked_user = mocker.Mock(roles=[enums.Role.VERIFIED])
    mocked_db_user = create_db_user(get_strike_points=total_points)
    res = await strike_service._apply_punishment(
        mocked_logging_embed, mocked_user, mocked_db_user, previous_points
    )

    assert res == expected_punishment


@pytest.mark.parametrize(
    "user_id,total_points,strike_params,expected_result",
    [
        (
            "1",
            "1",
            [("1", enums.StrikeSeverity.MINOR, "test", "1")],
            "Strikes found for <@1>: [Temporary points: None | Permanent points: None]"
            "\n* ID: 1 | SEVERITY: 1 | Moderator: <@1> | REASON: test"
            "\nTotal Points: 1",
        ),
        (
            "1",
            "3",
            [
                ("1", enums.StrikeSeverity.MINOR, "test", "1"),
                ("2", enums.StrikeSeverity.MODERATE, "test2", "3"),
            ],
            "Strikes found for <@1>: [Temporary points: None | Permanent points: None]"
            "\n* ID: 1 | SEVERITY: 1 | Moderator: <@1> | REASON: test"
            "\n* ID: 2 | SEVERITY: 2 | Moderator: <@3> | REASON: test2"
            "\nTotal Points: 3",
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_user_strikes(
    user_id: str,
    total_points: str,
    strike_params: List[tuple],
    expected_result: str,
    mocker: MockerFixture,
    create_db_user,
):
    mocked_user = mocker.Mock(id=user_id)
    mocked_db_user = create_db_user(get_strike_points=total_points)
    mocker.patch(
        "moddingway.database.users_database.get_user", return_value=mocked_db_user
    )
    mocker.patch(
        "moddingway.database.strikes_database.list_strikes", return_value=strike_params
    )
    res = await strike_service.get_user_strikes(mocked_user)
    assert res == expected_result


@pytest.mark.asyncio
async def test_add_strike(create_db_user,mocker:MockerFixture):

    mocked_db_user = create_db_user(user_id=1,temporary_points=0,get_strike_points=0)

    mocked_user = mocker.Mock(spec=discord.Member, id=1)

    mocked_author = mocker.Mock(spec=discord.Member)
    mocked_author.id = 2

    mocked_logging_embed = mocker.Mock(spec=discord.Embed)
    mocked_logging_embed.add_field = mocker.Mock()
    mocked_logging_embed.set_footer = mocker.Mock()

    

    mocked_get_user = mocker.patch("moddingway.database.users_database.get_user", return_value=mocked_db_user)
    mocked_add_strike = mocker.patch("moddingway.database.strikes_database.add_strike",return_value=1)
    
    mocked_strike = mocker.Mock()
    mocked_strike_class = mocker.patch(
        "moddingway.services.strike_service.Strike",
        autospec=True,
        return_value=mocked_strike
    )
    
    mocked_update_user_strike_points = mocker.patch("moddingway.database.users_database.update_user_strike_points", return_value=None)
    
    mocked_punishment = mocker.Mock()
    mocked__apply_punishment = mocker.patch("moddingway.services.strike_service._apply_punishment",return_value=mocked_punishment)

    await strike_service.add_strike(logging_embed=mocked_logging_embed,user=mocked_user,severity=enums.StrikeSeverity.MODERATE,reason="test",author=mocked_author)

    mocked_get_user.assert_called_with(mocked_user.id)

    mocked_strike_class.assert_called_with(
        user_id=mocked_user.id,
        severity=enums.StrikeSeverity.MODERATE,
        reason="test",
        created_timestamp=mocker.ANY, 
        created_by=str(mocked_author.id),
        last_edited_timestamp=mocker.ANY, 
        last_edited_by=str(mocked_author.id)
    )

    mocked_add_strike.assert_called_with(mocked_strike)

    mocked_update_user_strike_points.assert_called_with(mocked_db_user)

    mocked__apply_punishment.assert_called_with(
        mocked_logging_embed,
        mocked_user,
        mocked_db_user,
        0
    )