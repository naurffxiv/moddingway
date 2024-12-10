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


@pytest.fixture
def create_role(mocker):
    def __create_role(name: str):
        mocked_role = mocker.Mock()
        mocked_role.name = name
        return mocked_role

    return __create_role


@pytest.mark.parametrize(
    "input_role_names,role,expected_result",
    [
        ([], enums.Role.VERIFIED, False),
        (["Mod"], enums.Role.VERIFIED, False),
        (["Verified"], enums.Role.VERIFIED, True),
        (["Mod", "Verified"], enums.Role.VERIFIED, True),
    ],
)
def test_user_has_role(
    input_role_names: List[str],
    role: enums.Role,
    expected_result: bool,
    mocker: MockerFixture,
    create_role,
):
    roles = [create_role(name=role_name) for role_name in input_role_names]
    mocked_member = mocker.Mock(roles=roles)

    res = util.user_has_role(mocked_member, role)

    assert res == expected_result


