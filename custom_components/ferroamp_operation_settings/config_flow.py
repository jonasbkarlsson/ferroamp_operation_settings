"""Adds config flow for Ferroamp Operation Settings."""
import logging
import voluptuous as vol

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_DEVICE_NAME,
    CONF_LOGIN_EMAIL,
    CONF_LOGIN_PASSWORD,
    CONF_SYSTEM_ID,
    DOMAIN,
)
from .helpers.config_flow import DeviceNameCreator, FlowValidator

_LOGGER = logging.getLogger(__name__)


class FerroampOperationSettingsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow."""

    VERSION = 1

    def __init__(self):
        """Initialize."""
        _LOGGER.debug("FerroampOperationSettingsConfigFlow.__init__")
        self._errors = {}
        self.user_input = {}

    async def async_step_user(self, user_input=None):
        _LOGGER.debug("FerroampOperationSettingsConfigFlow.async_step_user")
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #    return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            user_input = {}
            # Provide defaults for form
            user_input[CONF_DEVICE_NAME] = DeviceNameCreator.create(self.hass)
            user_input[CONF_SYSTEM_ID] = ""
            user_input[CONF_LOGIN_EMAIL] = ""
            user_input[CONF_LOGIN_PASSWORD] = ""

        else:
            # process user_input
            error = FlowValidator.validate_step_user(self.hass, user_input)
            if error is not None:
                self._errors[error[0]] = error[1]

            if not self._errors:
                self.user_input = user_input
                return self.async_create_entry(
                    title=self.user_input[CONF_DEVICE_NAME], data=self.user_input
                )

        return await self._show_config_form_user(user_input)

    async def _show_config_form_user(self, user_input):
        """Show the configuration form."""

        user_schema = {
            vol.Required(
                CONF_DEVICE_NAME, default=user_input[CONF_DEVICE_NAME]
            ): cv.string,
            vol.Required(
                CONF_SYSTEM_ID, default=user_input[CONF_SYSTEM_ID]
            ): cv.positive_int,
            vol.Required(
                CONF_LOGIN_EMAIL, default=user_input[CONF_LOGIN_EMAIL]
            ): cv.string,
            vol.Required(
                CONF_LOGIN_PASSWORD, default=user_input[CONF_LOGIN_PASSWORD]
            ): cv.string,
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(user_schema),
            errors=self._errors,
            last_step=True,
        )
