"""Coordinator for Ferroamp Operation Settings"""

import logging
from homeassistant.config_entries import (
    ConfigEntry,
)
from homeassistant.core import HomeAssistant, callback, Event
from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
from homeassistant.helpers.device_registry import async_get as async_device_registry_get
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.entity_registry import async_get as async_entity_registry_get
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
    async_entries_for_config_entry,
)


_LOGGER = logging.getLogger(__name__)


class FerroampOperationSettingsCoordinator:
    """Coordinator class"""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize."""
        self.hass = hass
        self.config_entry = config_entry
        self.listeners = []
        self.platforms = []

        self.number_ace_threshold = None
        self.number_discharge_threshold = None
        self.number_charge_threshold = None
        self.number_import_threshold = None
        self.number_export_threshold = None
        self.number_discharge_reference = None
        self.number_charge_reference = None
        self.number_lower_reference = None
        self.number_upper_reference = None

        self.switch_pv = None
        self.switch_ace = None
        self.switch_limit_import = None
        self.switch_limit_export = None

        # Listen for changes to the device.
        self.listeners.append(
            hass.bus.async_listen(EVENT_DEVICE_REGISTRY_UPDATED, self.device_updated)
        )

    def unsubscribe_listeners(self):
        """Unsubscribed to listeners"""
        for unsub in self.listeners:
            unsub()

    @callback
    async def device_updated(self, event: Event):  # pylint: disable=unused-argument
        """Called when device is updated"""
        _LOGGER.debug("FerroampOperationSettings   Coordinator.device_updated()")
        if "device_id" in event.data:
            entity_registry: EntityRegistry = async_entity_registry_get(self.hass)
            all_entities = async_entries_for_config_entry(
                entity_registry, self.config_entry.entry_id
            )
            if all_entities:
                device_id = all_entities[0].device_id
                if event.data["device_id"] == device_id:
                    if "changes" in event.data:
                        if "name_by_user" in event.data["changes"]:
                            # If the device name is changed, update the integration name
                            device_registry: DeviceRegistry = async_device_registry_get(
                                self.hass
                            )
                            device = device_registry.async_get(device_id)
                            if device.name_by_user != self.config_entry.title:
                                self.hass.config_entries.async_update_entry(
                                    self.config_entry, title=device.name_by_user
                                )

    async def switch_pv_update(self, state: bool):
        """Handle the PV switch"""
        self.switch_pv = state
        _LOGGER.debug("switch_pv_update = %s", state)

    async def switch_ace_update(self, state: bool):
        """Handle the ACE switch"""
        self.switch_ace = state
        _LOGGER.debug("switch_ace_update = %s", state)

    async def switch_limit_import_update(self, state: bool):
        """Handle the Limit Import switch"""
        self.switch_limit_import = state
        _LOGGER.debug("switch_limit_import_update = %s", state)

    async def switch_limit_export_update(self, state: bool):
        """Handle the Limit Export switch"""
        self.switch_limit_export = state
        _LOGGER.debug("switch_limit_export_update = %s", state)

    def get_entity_id_from_unique_id(self, unique_id: str) -> str:
        """Get the Entity ID for the entity with the unique_id"""
        entity_registry: EntityRegistry = async_entity_registry_get(self.hass)
        all_entities = async_entries_for_config_entry(
            entity_registry, self.config_entry.entry_id
        )
        entity = [entity for entity in all_entities if entity.unique_id == unique_id]
        if len(entity) == 1:
            return entity[0].entity_id

        return None
