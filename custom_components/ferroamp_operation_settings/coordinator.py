"""Coordinator for Ferroamp Operation Settings"""

from datetime import datetime, timedelta
import logging
from typing import Any
from collections.abc import Callable, Coroutine
from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import (
    ConfigEntry,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback, Event, HassJob
from homeassistant.helpers.device_registry import EVENT_DEVICE_REGISTRY_UPDATED
from homeassistant.helpers.device_registry import async_get as async_device_registry_get
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.entity_registry import async_get as async_entity_registry_get
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
    async_entries_for_config_entry,
)
from homeassistant.helpers.event import (
    async_call_later,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


from custom_components.ferroamp_operation_settings.const import (
    BATTERY_CHARGE,
    BATTERY_DISCHARGE,
    BATTERY_OFF,
    DOMAIN,
    MODE_DEFAULT,
    MODE_PEAK_SHAVING,
    MODE_SELF_CONSUMPTION,
    STATUS_READY,
    STATUS_FAILED,
    STATUS_SUCCESS,
)

from custom_components.ferroamp_operation_settings.helpers.api import (
    FerroampApiClient,
)


_LOGGER = logging.getLogger(__name__)


class FerroampOperationSettingsCoordinator(DataUpdateCoordinator):
    """Coordinator class"""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: FerroampApiClient,
    ) -> None:
        """Initialize."""
        # Do not pull with regular intervals
        super().__init__(hass, _LOGGER, name=DOMAIN)

        self.hass = hass
        self.config_entry = config_entry
        self.api = client
        self.listeners = []
        self.platforms = []
        self.platforms_started = []

        self.number_ace_threshold: NumberEntity = None
        self.number_discharge_threshold: NumberEntity = None
        self.number_charge_threshold: NumberEntity = None
        self.number_import_threshold: NumberEntity = None
        self.number_export_threshold: NumberEntity = None
        self.number_discharge_reference: NumberEntity = None
        self.number_charge_reference: NumberEntity = None
        self.number_lower_reference: NumberEntity = None
        self.number_upper_reference: NumberEntity = None

        self.select_mode: SelectEntity = None
        self.select_battery_power_mode: SelectEntity = None

        self.switch_pv: SwitchEntity = None
        self.switch_ace: SwitchEntity = None
        self.switch_limit_import: SwitchEntity = None
        self.switch_limit_export: SwitchEntity = None

        self.sensor_status: SensorEntity = None

        # Listen for changes to the device.
        self.listeners.append(
            hass.bus.async_listen(EVENT_DEVICE_REGISTRY_UPDATED, self.device_updated)
        )

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

    def async_call_later_local(
        self,
        hass: HomeAssistant,
        delay: float | timedelta,
        action: (
            HassJob[[datetime], Coroutine[Any, Any, None] | None]
            | Callable[[datetime], Coroutine[Any, Any, None] | None]
        ),
    ) -> CALLBACK_TYPE:
        """
        Add a listener that is called in <delay>.
        A local version of async_call_later() that can be patched by the test framework.
        """
        return async_call_later(hass, delay, action)

    async def platform_started(self, platform: str):
        """Register started platforms"""
        self.platforms_started.append(platform)
        if all(item in self.platforms_started for item in self.platforms):
            # Update entities when all platforms have started.
            self.async_call_later_local(self.hass, 5.0, self.update_entities)

    async def update_entities(
        self, date_time: datetime = None
    ):  # pylint: disable=unused-argument
        """Update entities"""
        _LOGGER.debug("update_entities() starts")

        if not self.data:
            _LOGGER.error("update_entities() no data!")
            return

        if self.data["emsConfig"]["data"]["mode"] == 2:
            await self.select_mode.async_select_option(MODE_PEAK_SHAVING)
        elif self.data["emsConfig"]["data"]["mode"] == 3:
            await self.select_mode.async_select_option(MODE_SELF_CONSUMPTION)
        else:
            await self.select_mode.async_select_option(MODE_DEFAULT)

        if self.data["emsConfig"]["data"]["grid"]["ace"]["mode"] == 1:
            await self.switch_ace.async_turn_on()
        else:
            await self.switch_ace.async_turn_off()
        if self.data["emsConfig"]["data"]["grid"]["limitExport"] is True:
            await self.switch_limit_export.async_turn_on()
        else:
            await self.switch_limit_export.async_turn_off()
        if self.data["emsConfig"]["data"]["grid"]["limitImport"] is True:
            await self.switch_limit_import.async_turn_on()
        else:
            await self.switch_limit_import.async_turn_off()
        if self.data["emsConfig"]["data"]["pv"]["mode"] == 1:
            await self.switch_pv.async_turn_on()
        else:
            await self.switch_pv.async_turn_off()

        await self.number_ace_threshold.async_set_native_value(
            self.data["emsConfig"]["data"]["grid"]["ace"]["threshold"]
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

        if self.select_mode.current_option == MODE_PEAK_SHAVING:
            # Peak Shaving is using Discharge and Charge Thresholds
            await self.number_discharge_threshold.async_set_native_value(
                self.data["emsConfig"]["data"]["grid"]["thresholds"]["high"]
            )
            await self.number_charge_threshold.async_set_native_value(
                self.data["emsConfig"]["data"]["grid"]["thresholds"]["low"]
            )
        else:
            # Default and Self Consumption are using Import and Export Thresholds
            await self.number_import_threshold.async_set_native_value(
                self.data["emsConfig"]["data"]["grid"]["thresholds"]["high"]
            )
            await self.number_export_threshold.async_set_native_value(
                self.data["emsConfig"]["data"]["grid"]["thresholds"]["low"]
            )

        if self.number_charge_reference.value > 0:
            await self.select_battery_power_mode.async_select_option(BATTERY_CHARGE)
        elif self.number_discharge_reference.value > 0:
            await self.select_battery_power_mode.async_select_option(BATTERY_DISCHARGE)
        else:
            await self.select_battery_power_mode.async_select_option(BATTERY_OFF)

        _LOGGER.debug("update_entities() ends")

    async def set_status_ready(
        self, date_time: datetime = None
    ):  # pylint: disable=unused-argument
        """Set status to Ready"""
        self.sensor_status.set_status(STATUS_READY)

    async def get_data(self):
        """Get configuration from Ferroamp system and updated entities"""
        _LOGGER.debug("get_data() starts")
        await self.async_refresh()
        if self.last_update_success:
            await self.update_entities()
            self.sensor_status.set_status(STATUS_SUCCESS)
            self.async_call_later_local(self.hass, 7.0, self.set_status_ready)
        else:
            self.sensor_status.set_status(STATUS_FAILED)
            _LOGGER.error("Get Data failed.")
        _LOGGER.debug("get_data() ends")

    async def update(self):
        """Update the Ferroamp system with the contents of the entities"""

        _LOGGER.debug("update() starts")

        if not self.last_update_success:
            _LOGGER.error("Get Data before Update!")
            return

        body = {}
        body["payload"] = {}
        body["payload"]["battery"] = {}
        body["payload"]["battery"]["powerRef"] = {}

        if self.select_mode.current_option == MODE_DEFAULT:
            if self.select_battery_power_mode.current_option == BATTERY_DISCHARGE:
                body["payload"]["battery"]["powerRef"][
                    "discharge"
                ] = self.number_discharge_reference.value
            else:
                body["payload"]["battery"]["powerRef"]["discharge"] = 0

            if self.select_battery_power_mode.current_option == BATTERY_CHARGE:
                body["payload"]["battery"]["powerRef"][
                    "charge"
                ] = self.number_charge_reference.value
            else:
                body["payload"]["battery"]["powerRef"]["charge"] = 0
        else:
            body["payload"]["battery"]["powerRef"][
                "discharge"
            ] = self.number_discharge_reference.value
            body["payload"]["battery"]["powerRef"][
                "charge"
            ] = self.number_charge_reference.value

        body["payload"]["battery"]["socRef"] = {}
        body["payload"]["battery"]["socRef"]["high"] = self.number_upper_reference.value
        body["payload"]["battery"]["socRef"]["low"] = self.number_lower_reference.value
        body["payload"]["pv"] = {}
        body["payload"]["pv"]["mode"] = int(self.switch_pv.is_on)
        body["payload"]["grid"] = {}
        body["payload"]["grid"]["limitExport"] = self.switch_limit_export.is_on

        body["payload"]["grid"]["thresholds"] = {}
        if self.select_mode.current_option == MODE_PEAK_SHAVING:
            # Peak Shaving is using Discharge and Charge Thresholds
            body["payload"]["grid"]["thresholds"][
                "high"
            ] = self.number_discharge_threshold.value
            body["payload"]["grid"]["thresholds"][
                "low"
            ] = self.number_charge_threshold.value
        else:
            # Default and Self Consumption are using Import and Export Thresholds
            body["payload"]["grid"]["thresholds"][
                "high"
            ] = self.number_import_threshold.value
            body["payload"]["grid"]["thresholds"][
                "low"
            ] = self.number_export_threshold.value

        body["payload"]["grid"]["limitImport"] = self.switch_limit_import.is_on

        body["payload"]["grid"]["ace"] = {}
        body["payload"]["grid"]["ace"]["threshold"] = self.number_ace_threshold.value
        body["payload"]["grid"]["ace"]["mode"] = int(self.switch_ace.is_on)

        if self.select_mode.current_option == MODE_PEAK_SHAVING:
            body["payload"]["mode"] = 2
        elif self.select_mode.current_option == MODE_SELF_CONSUMPTION:
            body["payload"]["mode"] = 3
        else:
            # Default mode
            body["payload"]["mode"] = 1

        _LOGGER.debug("body = %s", str(body))
        update_ok = await self.api.async_set_data(body)
        if update_ok:
            self.sensor_status.set_status(STATUS_SUCCESS)
            self.async_call_later_local(self.hass, 7.0, self.set_status_ready)
            _LOGGER.debug("update() OK")
        else:
            self.sensor_status.set_status(STATUS_FAILED)
            _LOGGER.error("Update failed.")
