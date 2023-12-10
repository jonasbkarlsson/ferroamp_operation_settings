"""Test ferroamp_operation_settings api."""

from custom_components.ferroamp_operation_settings.const import (
    CONF_LOGIN_EMAIL,
    CONF_LOGIN_PASSWORD,
    CONF_SYSTEM_ID,
)
from custom_components.ferroamp_operation_settings.helpers.api import (
    FerroampApiClient,
)

from tests.const import MOCK_CONFIG_ALL

# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.


# pylint: disable=unused-argument
# pylint: disable=protected-access
async def test_api_client(hass):
    """Test api client."""

    api_client: FerroampApiClient = FerroampApiClient(
        MOCK_CONFIG_ALL[CONF_SYSTEM_ID],
        MOCK_CONFIG_ALL[CONF_LOGIN_EMAIL],
        MOCK_CONFIG_ALL[CONF_LOGIN_PASSWORD],
        None,
    )

    assert await api_client.async_get_data()
    assert api_client._access_token is not None
    assert api_client._data is not None

    body = {}
    body["payload"] = {}
    body["payload"]["battery"] = {}
    body["payload"]["battery"]["powerRef"] = {}

    assert await api_client.async_set_data(body)

    # Remove access token
    api_client._access_token = None
    assert await api_client.async_set_data(body)
