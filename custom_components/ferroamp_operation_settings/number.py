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
    ENTITY_NAME_CHARGE_REFERENCE_NUMBER,
    ENTITY_NAME_CHARGE_THRESHOLD_NUMBER,
    ENTITY_NAME_DISCHARGE_REFERENCE_NUMBER,
    ENTITY_NAME_DISCHARGE_THRESHOLD_NUMBER,
    ENTITY_NAME_EXPORT_THRESHOLD_NUMBER,
    ENTITY_NAME_IMPORT_THRESHOLD_NUMBER,
    ENTITY_NAME_LOWER_REFERENCE_NUMBER,
    ENTITY_NAME_UPPER_REFERENCE_NUMBER,
    ICON_BATTERY_20,
    ICON_BATTERY_80,
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
    numbers.append(FerroampOperationSettingsNumberImportThreshold(entry, coordinator))
    numbers.append(FerroampOperationSettingsNumberExportThreshold(entry, coordinator))
    numbers.append(
        FerroampOperationSettingsNumberDischargeReference(entry, coordinator)
    )
    numbers.append(FerroampOperationSettingsNumberChargeReference(entry, coordinator))
    numbers.append(FerroampOperationSettingsNumberLowerReference(entry, coordinator))
    numbers.append(FerroampOperationSettingsNumberUpperReference(entry, coordinator))
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
    _attr_unit_of_measurement = "A"

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberACEThreshold.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.number_ace_threshold = self
        if self.value is None:
            self._attr_native_value = 16
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)


class FerroampOperationSettingsNumberDischargeThreshold(
    FerroampOperationSettingsNumber
):
    """Ferroamp Operation Settings Discharge Threshold number class."""

    _attr_name = ENTITY_NAME_DISCHARGE_THRESHOLD_NUMBER
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = -100000.0
    _attr_native_max_value = 100000.0
    _attr_native_step = 0.1
    _attr_unit_of_measurement = "W"

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberDischargeThreshold.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.number_discharge_threshold = self
        if self.value is None:
            self._attr_native_value = 0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)


class FerroampOperationSettingsNumberChargeThreshold(FerroampOperationSettingsNumber):
    """Ferroamp Operation Settings Charge Threshold number class."""

    _attr_name = ENTITY_NAME_CHARGE_THRESHOLD_NUMBER
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = -100000.0
    _attr_native_max_value = 100000.0
    _attr_native_step = 0.1
    _attr_unit_of_measurement = "W"

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberChargeThreshold.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.number_charge_threshold = self
        if self.value is None:
            self._attr_native_value = 0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)


class FerroampOperationSettingsNumberImportThreshold(FerroampOperationSettingsNumber):
    """Ferroamp Operation Settings Import Threshold number class."""

    _attr_name = ENTITY_NAME_IMPORT_THRESHOLD_NUMBER
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = -100000.0
    _attr_native_max_value = 100000.0
    _attr_native_step = 0.1
    _attr_unit_of_measurement = "W"

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberImportThreshold.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.number_import_threshold = self
        if self.value is None:
            self._attr_native_value = 0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)


class FerroampOperationSettingsNumberExportThreshold(FerroampOperationSettingsNumber):
    """Ferroamp Operation Settings Export Threshold number class."""

    _attr_name = ENTITY_NAME_EXPORT_THRESHOLD_NUMBER
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = -100000.0
    _attr_native_max_value = 100000.0
    _attr_native_step = 0.1
    _attr_unit_of_measurement = "W"

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberExportThreshold.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.number_export_threshold = self
        if self.value is None:
            self._attr_native_value = 0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)


class FerroampOperationSettingsNumberDischargeReference(
    FerroampOperationSettingsNumber
):
    """Ferroamp Operation Settings Discharge Reference number class."""

    _attr_name = ENTITY_NAME_DISCHARGE_REFERENCE_NUMBER
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 100000.0
    _attr_native_step = 0.1
    _attr_unit_of_measurement = "W"

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberDischargeReference.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.number_discharge_reference = self
        if self.value is None:
            self._attr_native_value = 0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)


class FerroampOperationSettingsNumberChargeReference(FerroampOperationSettingsNumber):
    """Ferroamp Operation Settings Charge Reference number class."""

    _attr_name = ENTITY_NAME_CHARGE_REFERENCE_NUMBER
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 100000.0
    _attr_native_step = 0.1
    _attr_unit_of_measurement = "W"

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberChargeReference.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.number_charge_reference = self
        if self.value is None:
            self._attr_native_value = 0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)


class FerroampOperationSettingsNumberLowerReference(FerroampOperationSettingsNumber):
    """Ferroamp Operation Settings Lower Reference number class."""

    _attr_name = ENTITY_NAME_LOWER_REFERENCE_NUMBER
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 100.0
    _attr_native_step = 0.1
    _attr_unit_of_measurement = "%"
    _attr_icon = ICON_BATTERY_20

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberLowerReference.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.number_lower_reference = self
        if self.value is None:
            self._attr_native_value = 0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)


class FerroampOperationSettingsNumberUpperReference(FerroampOperationSettingsNumber):
    """Ferroamp Operation Settings Upper Reference number class."""

    _attr_name = ENTITY_NAME_UPPER_REFERENCE_NUMBER
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 100.0
    _attr_native_step = 0.1
    _attr_unit_of_measurement = "%"
    _attr_icon = ICON_BATTERY_80

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsNumberUpperReference.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.number_upper_reference = self
        if self.value is None:
            self._attr_native_value = 0
            self.update_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await super().async_set_native_value(value)
