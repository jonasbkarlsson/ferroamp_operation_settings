"""Test ferroamp_operation_settings api."""
from datetime import datetime
from http.cookies import Morsel, SimpleCookie
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ferroamp_operation_settings import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.ferroamp_operation_settings.coordinator import (
    FerroampOperationSettingsCoordinator,
)
from custom_components.ferroamp_operation_settings.const import DOMAIN
from custom_components.ferroamp_operation_settings.helpers.api import Cookie

from tests.const import MOCK_CONFIG_ALL

# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.


# pylint: disable=unused-argument
async def test_api(hass):
    """Test api."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test", title="none"
    )
    config_entry.add_to_hass(hass)

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be.
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroampOperationSettingsCoordinator
    )

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_cookies(hass):
    """Test cookies."""

    cookies = None
    assert Cookie.get_first_cookie(cookies) is None
    cookies: SimpleCookie = SimpleCookie()
    assert Cookie.get_first_cookie(cookies) is None
    cookie: Morsel = Morsel()
    cookie.set(key="access_token", val="abcdef", coded_val=None)
    cookie["expires"] = "Sun, 12 Nov 2023 22:19:28 GMT"
    cookies["access_token"] = cookie
    assert Cookie.get_first_cookie(cookies) is not None
    expires: datetime = Cookie.get_expires(cookie)
    assert expires.year == 2023
    assert expires.month == 11
    assert expires.day == 12
    assert expires.hour == 22
    assert expires.minute == 19
