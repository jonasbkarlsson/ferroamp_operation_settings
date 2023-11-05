"""Helpers for config_flow"""

import logging
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_device_registry_get
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.entity_registry import async_get as async_entity_registry_get
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
)


# pylint: disable=relative-beyond-top-level
from ..const import (
    DOMAIN,
    NAME,
)

_LOGGER = logging.getLogger(__name__)


class FlowValidator:
    """Validator of flows"""

    @staticmethod
    def validate_step_user(
        hass: HomeAssistant, user_input: dict[str, Any]
    ) -> list[str]:
        """Validate step_user"""

        entity_registry: EntityRegistry = async_entity_registry_get(hass)
        entities = entity_registry.entities

        # Validate System ID, login email and password
        #    _LOGGER.debug("Something is wrong")
        #    return ("base", "login_failed")

        return None


class DeviceNameCreator:
    """Class that creates the name of the new device"""

    @staticmethod
    def create(hass: HomeAssistant) -> str:
        """Create device name"""
        device_registry: DeviceRegistry = async_device_registry_get(hass)
        devices = device_registry.devices
        # Find existing Ferroamp Operation Settings devices
        ev_devices = []
        for device in devices:
            for item in devices[device].identifiers:
                if item[0] == DOMAIN:
                    ev_devices.append(device)
        # If this is the first device. just return NAME
        if len(ev_devices) == 0:
            return NAME
        # Find the highest number at the end of the name
        higest = 1
        for device in ev_devices:
            device_name: str = devices[device].name
            if device_name == NAME:
                pass
            else:
                try:
                    device_number = int(device_name[len(NAME) :])
                    if device_number > higest:
                        higest = device_number
                except ValueError:
                    pass
        # Add ONE to the highest value and append after NAME
        return f"{NAME} {higest+1}"
