import pytest
from pytest_mock.plugin import MockerFixture

from moddingway import enums


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
