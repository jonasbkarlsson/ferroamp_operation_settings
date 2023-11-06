"""Test ferroamp_operation_settings button."""
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import STATE_ON, STATE_OFF

from custom_components.ferroamp_operation_settings import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.ferroamp_operation_settings.coordinator import (
    FerroampOperationSettingsCoordinator,
)
from custom_components.ferroamp_operation_settings.const import BUTTON, DOMAIN
from custom_components.ferroamp_operation_settings.button import (
    FerroampOperationSettingsButtonGetData,
    FerroampOperationSettingsButtonUpdate,
)

from .const import MOCK_CONFIG_ALL

# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.


# pylint: disable=unused-argument
async def test_button(hass):
    """Test buttons."""
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
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Get the buttons
    button_get_data: FerroampOperationSettingsButtonGetData = hass.data[
        "entity_components"
    ][BUTTON].get_entity("button.none_get_data")
    button_update: FerroampOperationSettingsButtonUpdate = hass.data[
        "entity_components"
    ][BUTTON].get_entity("button.none_update")
    assert button_get_data
    assert button_update
    assert isinstance(button_get_data, FerroampOperationSettingsButtonGetData)
    assert isinstance(button_update, FerroampOperationSettingsButtonUpdate)

    # TODO: Test the butttons
    await button_get_data.async_press()
    await button_update.async_press()

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]
