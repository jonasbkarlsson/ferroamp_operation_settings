"""Select platform for Ferroamp Operation Settings."""
import logging
from typing import Union

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    BATTERY_POWER_MODES,
    DOMAIN,
    ENTITY_NAME_BATTERY_POWER_MODE_SELECT,
    ENTITY_NAME_MODE_SELECT,
    ICON,
    ICON_BATTERY_50,
    MODES,
    SELECT,
)
from .coordinator import FerroampOperationSettingsCoordinator
from .entity import FerroampOperationSettingsEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_devices
):  # pylint: disable=unused-argument
    """Setup select platform."""
    _LOGGER.debug("FerroampOperationSettings.select.py")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    selects = []
    selects.append(FerroampOperationSettingsSelectMode(entry, coordinator))
    selects.append(FerroampOperationSettingsSelectBatteryPowerMode(entry, coordinator))
    async_add_devices(selects)


class FerroampOperationSettingsSelect(
    FerroampOperationSettingsEntity, SelectEntity, RestoreEntity
):
    """Ferroamp Operation Settings switch class."""

    _attr_current_option: Union[str, None] = None  # Using Union to support Python 3.9

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsSelect.__init__()")
        super().__init__(entry)
        self.coordinator = coordinator
        id_name = self._attr_name.replace(" ", "").lower()
        self._attr_unique_id = ".".join([entry.entry_id, SELECT, id_name])

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        restored: State = await self.async_get_last_state()
        if restored is not None:
            await self.async_select_option(restored.state)


class FerroampOperationSettingsSelectMode(FerroampOperationSettingsSelect):
    """Ferroamp Operation Settings Mode select class."""

    _attr_name = ENTITY_NAME_MODE_SELECT
    _attr_icon = ICON
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = MODES

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsSelectMode.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.select_mode = self
        if self.state is None:
            self._attr_current_option = "Default"
            self.update_ha_state()


class FerroampOperationSettingsSelectBatteryPowerMode(FerroampOperationSettingsSelect):
    """Ferroamp Operation Settings Battery Power Mode select class."""

    _attr_name = ENTITY_NAME_BATTERY_POWER_MODE_SELECT
    _attr_icon = ICON_BATTERY_50
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = BATTERY_POWER_MODES

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsSelectBatteryPowerMode.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.select_battery_power_mode = self
        if self.state is None:
            self._attr_current_option = "Off"
            self.update_ha_state()
