"""Coordinator for Ferroamp Operation Settings"""

import logging
from homeassistant.components.number import NumberEntity
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
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


from custom_components.ferroamp_operation_settings.const import DOMAIN

from custom_components.ferroamp_operation_settings.helpers.api import ApiClientBase


_LOGGER = logging.getLogger(__name__)


class FerroampOperationSettingsCoordinator(DataUpdateCoordinator):
    """Coordinator class"""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, client: ApiClientBase
    ) -> None:
        """Initialize."""
        self.hass = hass
        self.config_entry = config_entry
        self.api = client
        self.listeners = []
        self.platforms = []

        self.number_ace_threshold: NumberEntity = None
        self.number_discharge_threshold: NumberEntity = None
        self.number_charge_threshold: NumberEntity = None
        self.number_import_threshold: NumberEntity = None
        self.number_export_threshold: NumberEntity = None
        self.number_discharge_reference: NumberEntity = None
        self.number_charge_reference: NumberEntity = None
        self.number_lower_reference: NumberEntity = None
        self.number_upper_reference: NumberEntity = None

        self.switch_pv = None
        self.switch_ace = None
        self.switch_limit_import = None
        self.switch_limit_export = None

        # Listen for changes to the device.
        self.listeners.append(
            hass.bus.async_listen(EVENT_DEVICE_REGISTRY_UPDATED, self.device_updated)
        )

        # Do not pull with regular intervals
        super().__init__(hass, _LOGGER, name=DOMAIN)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.api.async_get_data()
        except Exception as exception:
            raise UpdateFailed() from exception

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

    async def get_data(self):
        """Get configuration from Ferroamp system and updated entities"""
        await self.async_refresh()
        if self.last_update_success:
            await self.number_ace_threshold.async_set_native_value(
                self.data["emsConfig"]["data"]["grid"]["ace"]["threshold"]
            )
            await self.number_discharge_threshold.async_set_native_value(
                self.data["emsConfig"]["data"]["grid"]["thresholds"][
                    "high"
                ]  # Conditionally set
            )
            await self.number_charge_threshold.async_set_native_value(
                self.data["emsConfig"]["data"]["grid"]["thresholds"][
                    "low"
                ]  # Conditionally set
            )
            await self.number_import_threshold.async_set_native_value(
                self.data["emsConfig"]["data"]["grid"]["thresholds"][
                    "high"
                ]  # Conditionally set
            )
            await self.number_export_threshold.async_set_native_value(
                self.data["emsConfig"]["data"]["grid"]["thresholds"][
                    "low"
                ]  # Conditionally set
            )
            await self.number_discharge_reference.async_set_native_value(
                self.data["emsConfig"]["data"]["battery"]["powerRef"]["discharge"]
            )
            await self.number_charge_reference.async_set_native_value(
                self.data["emsConfig"]["data"]["battery"]["powerRef"]["charge"]
            )
            await self.number_lower_reference.async_set_native_value(
                self.data["emsConfig"]["data"]["battery"]["socRef"]["low"]
            )
            await self.number_upper_reference.async_set_native_value(
                self.data["emsConfig"]["data"]["battery"]["socRef"]["high"]
            )

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
