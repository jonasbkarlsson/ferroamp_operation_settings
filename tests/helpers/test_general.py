"""Test ferroamp_operation_settings/helpers/general.py"""


from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ferroamp_operation_settings.const import (
    CONF_SYSTEM_ID,
    CONF_LOGIN_EMAIL,
    CONF_LOGIN_PASSWORD,
)
from custom_components.ferroamp_operation_settings.helpers.general import (
    Validator,
    get_parameter,
)

from tests.helpers.const import MOCK_CONFIG_DATA, MOCK_CONFIG_OPTIONS


# pylint: disable=unused-argument
async def test_is_float(hass):
    """Test is_float"""

    assert isinstance(Validator.is_float("0"), bool)
    assert Validator.is_float("0") is True
    assert Validator.is_float("56.4") is True
    assert Validator.is_float("-34.3") is True
    assert Validator.is_float("a") is False
    assert Validator.is_float(None) is False
    assert Validator.is_float("") is False


async def test_get_parameter(hass):
    """Test get_parameter"""

    config_entry = MockConfigEntry(data=MOCK_CONFIG_DATA, options=MOCK_CONFIG_OPTIONS)
    config_entry.add_to_hass(hass)
    assert get_parameter(config_entry, CONF_SYSTEM_ID) == 1234
    assert get_parameter(config_entry, CONF_LOGIN_EMAIL) == "abc@d.e"
    assert get_parameter(config_entry, CONF_LOGIN_PASSWORD) is None
    assert get_parameter(config_entry, CONF_LOGIN_PASSWORD, "password") == "password"
