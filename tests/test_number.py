"""Test ferroamp_operation_settings number."""
from unittest.mock import patch
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.components.number import NumberExtraStoredData

from custom_components.ferroamp_operation_settings import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.ferroamp_operation_settings.const import (
    DOMAIN,
    NUMBER,
)
from custom_components.ferroamp_operation_settings.coordinator import (
    FerroampOperationSettingsCoordinator,
)
from custom_components.ferroamp_operation_settings.number import (
    FerroampOperationSettingsNumberACEThreshold,
    FerroampOperationSettingsNumberDischargeThreshold,
    FerroampOperationSettingsNumberChargeThreshold,
)

from .const import MOCK_CONFIG_ALL

# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.


# pylint: disable=unused-argument
async def test_number(hass):
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

    # Get the numbers
    number_ace_threshold: FerroampOperationSettingsNumberACEThreshold = hass.data[
        "entity_components"
    ][NUMBER].get_entity("number.none_ace_threshold")
    number_discharge_threshold: FerroampOperationSettingsNumberDischargeThreshold = (
        hass.data["entity_components"][NUMBER].get_entity(
            "number.none_discharge_threshold"
        )
    )
    number_charge_threshold: FerroampOperationSettingsNumberChargeThreshold = hass.data[
        "entity_components"
    ][NUMBER].get_entity("number.none_charge_threshold")
    assert number_ace_threshold
    assert number_discharge_threshold
    assert number_charge_threshold
    assert isinstance(number_ace_threshold, FerroampOperationSettingsNumberACEThreshold)
    assert isinstance(
        number_discharge_threshold, FerroampOperationSettingsNumberDischargeThreshold
    )
    assert isinstance(
        number_charge_threshold, FerroampOperationSettingsNumberChargeThreshold
    )

    # Test the numbers

    await number_ace_threshold.async_set_native_value(3.2)
    assert coordinator.number_ace_threshold == 3.2

    await number_discharge_threshold.async_set_native_value(123)
    assert coordinator.number_discharge_threshold == 123

    await number_charge_threshold.async_set_native_value(33)
    assert coordinator.number_charge_threshold == 33

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


@pytest.fixture(name="mock_last_state_number")
def mock_last_state_number_fixture():
    """Mock last state."""

    restored: NumberExtraStoredData = NumberExtraStoredData.from_dict(
        {
            "native_max_value": 100,
            "native_min_value": 0,
            "native_step": 1,
            "native_unit_of_measurement": None,
            "native_value": 55,
        }
    )
    with patch(
        "homeassistant.components.number.RestoreNumber.async_get_last_number_data",
        return_value=restored,
    ):
        yield


async def test_number_restore(hass: HomeAssistant, mock_last_state_number):
    """Test sensor properties."""

    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test", title="none"
    )
    config_entry.add_to_hass(hass)
    await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    number_ace_threshold: FerroampOperationSettingsNumberACEThreshold = hass.data[
        "entity_components"
    ][NUMBER].get_entity("number.none_ace_threshold")

    await number_ace_threshold.async_set_native_value(45)
    assert number_ace_threshold.native_value == 45

    await number_ace_threshold.async_added_to_hass()
    assert number_ace_threshold.native_value == 55

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    await hass.async_block_till_done()
    assert config_entry.entry_id not in hass.data[DOMAIN]
