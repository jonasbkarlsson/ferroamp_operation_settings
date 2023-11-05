"""Test ferroamp_operation_settings/helpers/config_flow.py"""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_device_registry_get
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.entity_registry import async_get as async_entity_registry_get
from homeassistant.helpers.entity_registry import EntityRegistry

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ferroamp_operation_settings.helpers.config_flow import (
    DeviceNameCreator,
)
from custom_components.ferroamp_operation_settings.const import (
    DOMAIN,
    NAME,
)

from tests.const import (
    MOCK_CONFIG_ALL,
)


async def test_validate_step_user_price(hass: HomeAssistant):
    """Test the price entity in test_validate_step_user."""

    entity_registry: EntityRegistry = async_entity_registry_get(hass)

    # Check with TBD
    # assert FlowValidator.validate_step_user(hass, MOCK_CONFIG_USER) == (
    #     "base",
    #     "something_wrong",
    # )

    assert True


async def test_device_name_creator(hass: HomeAssistant):
    """Test the FindEntity."""

    device_registry: DeviceRegistry = async_device_registry_get(hass)
    names = []

    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test")
    config_entry.add_to_hass(hass)
    assert (name := DeviceNameCreator.create(hass)) == NAME
    names.append(name)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        name=name,
        identifiers={(DOMAIN, config_entry.entry_id)},
    )

    config_entry2 = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test2"
    )
    config_entry2.add_to_hass(hass)
    assert (name2 := DeviceNameCreator.create(hass)) not in names
    names.append(name2)
    device_registry.async_get_or_create(
        config_entry_id=config_entry2.entry_id,
        name=name2,
        identifiers={(DOMAIN, config_entry2.entry_id)},
    )

    assert (name3 := DeviceNameCreator.create(hass)) not in names

    # Use incorrect device name to provoke ValueError
    name3 = f"{NAME} abc"
    config_entry3 = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ALL, entry_id="test3"
    )
    config_entry3.add_to_hass(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry3.entry_id,
        name=name3,
        identifiers={(DOMAIN, config_entry3.entry_id)},
    )
    assert (name4 := DeviceNameCreator.create(hass)) not in names
    assert NAME in name4
