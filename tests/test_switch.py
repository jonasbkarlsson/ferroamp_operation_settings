"""Test ferroamp_operation_settings switch."""
from unittest.mock import patch
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant, State

from custom_components.ferroamp_operation_settings import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.ferroamp_operation_settings.const import DOMAIN, SWITCH
from custom_components.ferroamp_operation_settings.coordinator import (
    FerroampOperationSettingsCoordinator,
)
from custom_components.ferroamp_operation_settings.switch import (
    FerroampOperationSettingsSwitchPV,
    FerroampOperationSettingsSwitchACE,
    FerroampOperationSettingsSwitchLimitImport,
    FerroampOperationSettingsSwitchLimitExport,
)

from .const import MOCK_CONFIG_ALL

# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.


# pylint: disable=unused-argument
async def test_switch(hass, bypass_validate_input_sensors):
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

    # Get the switches
    switch_pv: FerroampOperationSettingsSwitchPV = hass.data["entity_components"][
        SWITCH
    ].get_entity("switch.none_smart_charging_activated")
    switch_ace: FerroampOperationSettingsSwitchACE = hass.data["entity_components"][
        SWITCH
    ].get_entity("switch.none_apply_price_limit")
    switch_limit_import: FerroampOperationSettingsSwitchLimitImport = hass.data[
        "entity_components"
    ][SWITCH].get_entity("switch.none_continuous_charging_preferred")
    switch_limit_export: FerroampOperationSettingsSwitchLimitExport = hass.data[
        "entity_components"
    ][SWITCH].get_entity("switch.none_ev_connected")
    assert switch_pv
    assert switch_ace
    assert switch_limit_import
    assert switch_limit_export
    assert isinstance(switch_pv, FerroampOperationSettingsSwitchPV)
    assert isinstance(switch_ace, FerroampOperationSettingsSwitchACE)
    assert isinstance(switch_limit_import, FerroampOperationSettingsSwitchLimitImport)
    assert isinstance(switch_limit_export, FerroampOperationSettingsSwitchLimitExport)

    # Test the switches
    await switch_pv.async_turn_on()
    assert coordinator.switch_pv is True
    await switch_pv.async_turn_off()
    assert coordinator.switch_pv is False
    await switch_pv.async_turn_on()
    assert coordinator.switch_pv is True

    await switch_ace.async_turn_on()
    assert coordinator.switch_apply_limit is True
    await switch_ace.async_turn_off()
    assert coordinator.switch_apply_limit is False
    await switch_ace.async_turn_on()
    assert coordinator.switch_apply_limit is True

    await switch_limit_import.async_turn_on()
    assert coordinator.switch_limit_import is True
    await switch_limit_import.async_turn_off()
    assert coordinator.switch_limit_import is False
    await switch_limit_import.async_turn_on()
    assert coordinator.switch_limit_import is True

    await switch_limit_export.async_turn_on()
    assert coordinator.switch_limit_export is True
    await switch_limit_export.async_turn_off()
    assert coordinator.switch_limit_export is False
    await switch_limit_export.async_turn_on()
    assert coordinator.switch_limit_export is True

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


@pytest.fixture(name="mock_last_state_off")
def mock_last_state_off_fixture():
    """Mock last state."""

    restored = State(entity_id="switch.none_smart_charging_activated", state=STATE_OFF)
    with patch(
        "homeassistant.helpers.restore_state.RestoreEntity.async_get_last_state",
        return_value=restored,
    ):
        yield


async def test_switch_off_restore(
    hass: HomeAssistant, bypass_validate_input_sensors, mock_last_state_off
):
    """Test sensor properties."""

    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test", title="none"
    )
    config_entry.add_to_hass(hass)
    await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    switch_pv: FerroampOperationSettingsSwitchPV = hass.data["entity_components"][
        SWITCH
    ].get_entity("switch.none_smart_charging_activated")

    await switch_pv.async_turn_on()
    assert switch_pv.is_on is True

    await switch_pv.async_added_to_hass()
    assert switch_pv.is_on is False

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    await hass.async_block_till_done()
    assert config_entry.entry_id not in hass.data[DOMAIN]


@pytest.fixture(name="mock_last_state_on")
def mock_last_state_on_fixture():
    """Mock last state."""

    restored = State(entity_id="switch.none_smart_charging_activated", state=STATE_ON)
    with patch(
        "homeassistant.helpers.restore_state.RestoreEntity.async_get_last_state",
        return_value=restored,
    ):
        yield


async def test_switch_on_restore(
    hass: HomeAssistant, bypass_validate_input_sensors, mock_last_state_on
):
    """Test sensor properties."""

    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test", title="none"
    )
    config_entry.add_to_hass(hass)
    await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    switch_pv: FerroampOperationSettingsSwitchPV = hass.data["entity_components"][
        SWITCH
    ].get_entity("switch.none_smart_charging_activated")

    await switch_pv.async_turn_on()
    assert switch_pv.is_on is True

    await switch_pv.async_added_to_hass()
    assert switch_pv.is_on is True

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    await hass.async_block_till_done()
    assert config_entry.entry_id not in hass.data[DOMAIN]
