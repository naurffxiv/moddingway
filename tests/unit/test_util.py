from datetime import timedelta
from typing import List

import pytest
from pytest_mock.plugin import MockerFixture

from moddingway import enums, util

single_line_case = ("short message", 100, ["short message"])
medium_len_case = (
    "medium length message that gets broken in half",
    35,
    ["medium length message that gets", "broken in half"],
)
exact_length_case = ("first secon third", 5, ["first", "secon", "third"])


@pytest.mark.parametrize(
    "input,max_chunk_length,output_array",
    [
        single_line_case,
        medium_len_case,
        exact_length_case,
    ],
)
def test_chunk_message(input: str, max_chunk_length: int, output_array: List[str]):
    res = []

    for line in util.chunk_message(input, max_chunk_length):
        res.append(line)

    assert res == output_array


@pytest.mark.parametrize(
    "input,expect",
    [
        (None, None),
        ("1h", None),
        ("100hour", None),
        ("15sec", timedelta(seconds=15)),
        ("55min", timedelta(minutes=55)),
        ("1hour", timedelta(hours=1)),
        ("3day", timedelta(days=3)),
    ],
)
def test_calculate_time_delta(input, expect):
    res = util.calculate_time_delta(input)

    if expect is None:
        assert res is None
    else:
        assert res == expect


@pytest.mark.parametrize(
    "input_roles,role,expected_result",
    [
        ([], enums.Role.VERIFIED, False),
        ([enums.Role.MOD], enums.Role.VERIFIED, False),
        ([enums.Role.VERIFIED], enums.Role.VERIFIED, True),
        ([enums.Role.MOD, enums.Role.VERIFIED], enums.Role.VERIFIED, True),
    ],
)
def test_user_has_role(
    input_roles: List[enums.Role],
    role: enums.Role,
    expected_result: bool,
    create_member,
):
    mocked_member = create_member(roles=input_roles)

    res = util.user_has_role(mocked_member, role)

    assert res == expected_result


async def test_add_and_remove_role(create_member):
    role_to_add = enums.Role.EXILED
    role_to_remove = enums.Role.VERIFIED

    mocked_member = create_member(roles=[enums.Role.VERIFIED])

    await util.add_and_remove_role(mocked_member, role_to_add, role_to_remove)

    mocked_member.add_roles.assert_called_once()
    mocked_member.remove_roles.assert_called_once()

    added_role = mocked_member.add_roles.call_args[0][0]
    assert added_role.name == role_to_add.value

    removed_role = mocked_member.remove_roles.call_args[0][0]
    assert removed_role.name == role_to_remove.value
