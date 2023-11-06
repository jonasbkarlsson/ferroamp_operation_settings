"""Button platform for Ferroamp Operation Settings."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant

from .const import (
    BUTTON,
    DOMAIN,
    ENTITY_NAME_GET_DATA_BUTTON,
    ENTITY_NAME_UPDATE_BUTTON,
    ICON_DOWNLOAD,
    ICON_UPDATE,
)
from .coordinator import FerroampOperationSettingsCoordinator
from .entity import FerroampOperationSettingsEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_devices):
    """Setup button platform."""
    _LOGGER.debug("FerroampOperationSettings.button.py")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    buttons = []
    buttons.append(FerroampOperationSettingsButtonGetData(entry, coordinator))
    buttons.append(FerroampOperationSettingsButtonUpdate(entry, coordinator))
    async_add_devices(buttons)


class FerroampOperationSettingsButton(FerroampOperationSettingsEntity, ButtonEntity):
    """Ferroamp Operation Settings button class."""

    def __init__(self, entry, coordinator: FerroampOperationSettingsCoordinator):
        _LOGGER.debug("FerroampOperationSettingsButton.__init__()")
        super().__init__(entry)
        self.coordinator = coordinator
        id_name = self._attr_name.replace(" ", "").lower()
        self._attr_unique_id = ".".join([entry.entry_id, BUTTON, id_name])
        _LOGGER.debug("self._attr_unique_id = %s", self._attr_unique_id)


class FerroampOperationSettingsButtonGetData(FerroampOperationSettingsButton):
    """Ferroamp Operation Settings GetData button class."""

    _attr_name = ENTITY_NAME_GET_DATA_BUTTON
    _attr_icon = ICON_DOWNLOAD

    async def async_press(self) -> None:
        """Press the button."""
        # TODO: await self.coordinator.turn_on_charging()
        pass


class FerroampOperationSettingsButtonUpdate(FerroampOperationSettingsButton):
    """Ferroamp Operation Settings Update button class."""

    _attr_name = ENTITY_NAME_UPDATE_BUTTON
    _attr_icon = ICON_UPDATE

    async def async_press(self) -> None:
        """Press the button."""
        # TODO: await self.coordinator.turn_off_charging()
        pass
