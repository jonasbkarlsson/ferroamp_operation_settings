"""Number platform for Ferroamp Operation Settings."""
import logging
from typing import Union

from homeassistant.components.number import (
    RestoreNumber,
    NumberExtraStoredData,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory

from .const import (
    DOMAIN,
    ENTITY_NAME_ACE_THRESHOLD_NUMBER,
    ENTITY_NAME_CHARGE_THRESHOLD_NUMBER,
    ENTITY_NAME_DISCHARGE_THRESHOLD_NUMBER,
    NUMBER,
)
from .coordinator import FerroampOperationSettingsCoordinator
from .entity import FerroampOperationSettingsEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_devices
):  # pylint: disable=unused-argument
    """Setup number platform."""
    _LOGGER.debug("FerroampOperationSettings.number.py")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    numbers = []
    numbers.append(FerroampOperationSettingsNumberACEThreshold(entry, coordinator))
    numbers.append(
        FerroampOperationSettingsNumberDischargeThreshold(entry, coordinator)
    )
    numbers.append(FerroampOperationSettingsNumberChargeThreshold(entry, coordinator))
    async_add_devices(numbers)


class FerroampOperationSettingsNumber(FerroampOperationSettingsEntity, RestoreNumber):
    """Ferroamp Operation Settings number class."""

    # To support HA 2022.7
    _attr_native_value: Union[float, None] = None  # Using Union to support Python 3.9

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumber.__init__()")
        super().__init__(entry)
        self.coordinator = coordinator
        id_name = self._attr_name.replace(" ", "").lower()
        self._attr_unique_id = ".".join([entry.entry_id, NUMBER, id_name])

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        self._attr_native_value = value

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        _LOGGER.debug("FerroampOperationSettingsNumber.async_added_to_hass()")
        restored: NumberExtraStoredData = await self.async_get_last_number_data()
        if restored is not None:
            await self.async_set_native_value(restored.native_value)
            _LOGGER.debug(
                "FerroampOperationSettingsNumber.async_added_to_hass() %s",
                self._attr_native_value,
            )


class FerroampOperationSettingsNumberACEThreshold(FerroampOperationSettingsNumber):
    """Ferroamp Operation Settings ACE Threshold number class."""

    _attr_name = ENTITY_NAME_ACE_THRESHOLD_NUMBER
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 100.0
    _attr_native_step = 0.1

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberACEThreshold.__init__()")
        super().__init__(entry, coordinator)
        if self.value is None:
            self._attr_native_value = 16
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)
        self.coordinator.number_ace_threshold = value


class FerroampOperationSettingsNumberDischargeThreshold(
    FerroampOperationSettingsNumber
):
    """Ferroamp Operation Settings Discharge Threshold number class."""

    _attr_name = ENTITY_NAME_DISCHARGE_THRESHOLD_NUMBER
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 100000.0
    _attr_native_step = 0.1

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberDischargeThreshold.__init__()")
        super().__init__(entry, coordinator)
        if self.value is None:
            self._attr_native_value = 0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)
        self.coordinator.number_discharge_threshold = value


class FerroampOperationSettingsNumberChargeThreshold(FerroampOperationSettingsNumber):
    """Ferroamp Operation Settings Charge Threshold number class."""

    _attr_name = ENTITY_NAME_CHARGE_THRESHOLD_NUMBER
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 100000.0
    _attr_native_step = 0.1

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberChargeThreshold.__init__()")
        super().__init__(entry, coordinator)
        if self.value is None:
            self._attr_native_value = 0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)
        self.coordinator.number_charge_threshold = value
