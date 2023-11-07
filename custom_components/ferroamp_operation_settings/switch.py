"""Switch platform for Ferroamp Operation Settings."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN,
    ENTITY_NAME_ACE_SWITCH,
    ENTITY_NAME_LIMIT_EXPORT_SWITCH,
    ENTITY_NAME_LIMIT_IMPORT_SWITCH,
    ENTITY_NAME_PV_SWITCH,
    ICON_SOLAR_POWER,
    SWITCH,
)
from .coordinator import FerroampOperationSettingsCoordinator
from .entity import FerroampOperationSettingsEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_devices
):  # pylint: disable=unused-argument
    """Setup switch platform."""
    _LOGGER.debug("FerroampOperationSettings.switch.py")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    switches = []
    switches.append(FerroampOperationSettingsSwitchPV(entry, coordinator))
    switches.append(FerroampOperationSettingsSwitchACE(entry, coordinator))
    switches.append(FerroampOperationSettingsSwitchLimitImport(entry, coordinator))
    switches.append(FerroampOperationSettingsSwitchLimitExport(entry, coordinator))
    async_add_devices(switches)


class FerroampOperationSettingsSwitch(
    FerroampOperationSettingsEntity, SwitchEntity, RestoreEntity
):
    """Ferroamp Operation Settings switch class."""

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsSwitch.__init__()")
        super().__init__(entry)
        self.coordinator = coordinator
        id_name = self._attr_name.replace(" ", "").lower()
        self._attr_unique_id = ".".join([entry.entry_id, SWITCH, id_name])

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        restored: State = await self.async_get_last_state()
        if restored is not None:
            if restored.state == STATE_ON:
                await self.async_turn_on()
            else:
                await self.async_turn_off()


class FerroampOperationSettingsSwitchPV(FerroampOperationSettingsSwitch):
    """Ferroamp Operation Settings PV switch class."""

    _attr_name = ENTITY_NAME_PV_SWITCH
    _attr_icon = ICON_SOLAR_POWER

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsSwitchPV.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.switch_pv = self
        if self.is_on is None:
            self._attr_is_on = True
            self.update_ha_state()


class FerroampOperationSettingsSwitchACE(FerroampOperationSettingsSwitch):
    """Ferroamp Operation Settings ACE switch class."""

    _attr_name = ENTITY_NAME_ACE_SWITCH

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsSwitchACE.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.switch_ace = self
        if self.is_on is None:
            self._attr_is_on = True
            self.update_ha_state()


class FerroampOperationSettingsSwitchLimitImport(FerroampOperationSettingsSwitch):
    """Ferroamp Operation Settings limit import switch class."""

    _attr_name = ENTITY_NAME_LIMIT_IMPORT_SWITCH

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsSwitchLimitImport.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.switch_limit_import = self
        if self.is_on is None:
            self._attr_is_on = False
            self.update_ha_state()


class FerroampOperationSettingsSwitchLimitExport(FerroampOperationSettingsSwitch):
    """Ferroamp Operation Settings limit export switch class."""

    _attr_name = ENTITY_NAME_LIMIT_EXPORT_SWITCH

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsSwitchLimitExport.__init__()")
        super().__init__(entry, coordinator)
        self.coordinator.switch_limit_export = self
        if self.is_on is None:
            self._attr_is_on = False
            self.update_ha_state()
