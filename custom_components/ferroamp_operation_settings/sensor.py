"""Sensor platform for Ferroamp Operation Settings."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

from custom_components.ferroamp_operation_settings.coordinator import (
    FerroampOperationSettingsCoordinator,
)


from .const import (
    DOMAIN,
    ENTITY_NAME_STATUS_SENSOR,
    ICON_INFORMATION,
    SENSOR,
    STATUS_READY,
)
from .entity import FerroampOperationSettingsEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Setup sensor platform."""
    _LOGGER.debug("FerroampOperationSettings.sensor.py")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []
    sensors.append(FerroampOperationSettingsSensorStatus(entry, coordinator))
    async_add_devices(sensors)
    await coordinator.platform_started(SENSOR)


class FerroampOperationSettingsSensor(FerroampOperationSettingsEntity, SensorEntity):
    """Ferroamp Operation Settings sensor class."""

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsSensor.__init__()")
        super().__init__(entry)
        self.coordinator = coordinator
        id_name = self._attr_name.replace(" ", "").lower()
        self._attr_unique_id = ".".join([entry.entry_id, SENSOR, id_name])

    @SensorEntity.native_value.setter
    def native_value(self, new_value):
        """Set the value reported by the sensor."""
        self._attr_native_value = new_value
        self.update_ha_state()


class FerroampOperationSettingsSensorStatus(FerroampOperationSettingsSensor):
    """Ferroamp Operation Settings sensor class."""

    _attr_name = ENTITY_NAME_STATUS_SENSOR
    _attr_icon = ICON_INFORMATION

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsSensorStatus.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.sensor_status = self

        self._attr_native_value = STATUS_READY
