"""Test ferroamp_operation_settings select."""
from unittest.mock import patch
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant, State

from custom_components.ferroamp_operation_settings import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.ferroamp_operation_settings.const import (
    DOMAIN,
    SELECT,
)
from custom_components.ferroamp_operation_settings.coordinator import (
    FerroampOperationSettingsCoordinator,
)
from custom_components.ferroamp_operation_settings.select import (
    FerroampOperationSettingsSelectMode,
    FerroampOperationSettingsSelectBatteryPowerMode,
)

from .const import MOCK_CONFIG_ALL

# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.


# pylint: disable=unused-argument
async def test_select(hass):
    """Test sensor properties."""
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

    # Get the selects
    select_mode: FerroampOperationSettingsSelectMode = hass.data["entity_components"][
        SELECT
    ].get_entity("select.none_mode")
    select_battery_power_mode: FerroampOperationSettingsSelectBatteryPowerMode = (
        hass.data["entity_components"][SELECT].get_entity(
            "select.none_battery_power_mode"
        )
    )
    assert select_mode
    assert select_battery_power_mode
    assert isinstance(select_mode, FerroampOperationSettingsSelectMode)
    assert isinstance(
        select_battery_power_mode, FerroampOperationSettingsSelectBatteryPowerMode
    )

    # Test the selects

    # TODO:

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


@pytest.fixture(name="mock_last_state_select")
def mock_last_state_select_fixture():
    """Mock last state."""

    restored: State = State(
        entity_id="select.none_charge_completion_time", state="Discharge"
    )
    with patch(
        "homeassistant.helpers.restore_state.RestoreEntity.async_get_last_state",
        return_value=restored,
    ):
        yield


async def test_select_restore(hass: HomeAssistant, mock_last_state_select):
    """Test sensor properties."""

    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test", title="none"
    )
    config_entry.add_to_hass(hass)
    await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    select_battery_power_mode: FerroampOperationSettingsSelectBatteryPowerMode = (
        hass.data["entity_components"][SELECT].get_entity(
            "select.none_battery_power_mode"
        )
    )

    await select_battery_power_mode.async_select_option("Charge")
    assert select_battery_power_mode.state == "Charge"

    await select_battery_power_mode.async_added_to_hass()
    assert select_battery_power_mode.state == "Discharge"

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    await hass.async_block_till_done()
    assert config_entry.entry_id not in hass.data[DOMAIN]
