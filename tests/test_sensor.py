"""Test ferroamp_operation_settings sensor."""
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import MAJOR_VERSION, MINOR_VERSION
from homeassistant.config_entries import ConfigEntryState

from custom_components.ferroamp_operation_settings import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.ferroamp_operation_settings.coordinator import (
    FerroampOperationSettingsCoordinator,
)
from custom_components.ferroamp_operation_settings.const import SENSOR, DOMAIN
from custom_components.ferroamp_operation_settings.sensor import (
    FerroampOperationSettingsSensorStatus,
)

from .const import MOCK_CONFIG_ALL

# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.


# pylint: disable=unused-argument
async def test_sensor(hass):
    """Test sensors."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test", title="none"
    )
    if MAJOR_VERSION > 2024 or (MAJOR_VERSION == 2024 and MINOR_VERSION >= 7):
        config_entry.mock_state(hass=hass, state=ConfigEntryState.LOADED)
    config_entry.add_to_hass(hass)

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be.
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert isinstance(
        hass.data[DOMAIN][config_entry.entry_id], FerroampOperationSettingsCoordinator
    )

    # Get the sensor
    sensor_status: FerroampOperationSettingsSensorStatus = hass.data[
        "entity_components"
    ][SENSOR].get_entity("sensor.none_status")
    assert sensor_status
    assert isinstance(sensor_status, FerroampOperationSettingsSensorStatus)

    # TODO: Test the sensor

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]
