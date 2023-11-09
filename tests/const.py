"""Constants for ferroamp_operation_settings tests."""
from custom_components.ferroamp_operation_settings.const import (
    CONF_DEVICE_NAME,
    CONF_LOGIN_EMAIL,
    CONF_LOGIN_PASSWORD,
    CONF_SYSTEM_ID,
)

# Mock config data to be used across multiple tests
MOCK_CONFIG_ALL = {
    CONF_DEVICE_NAME: "Ferroamp Operation Settings",
    CONF_SYSTEM_ID: 1234,
    CONF_LOGIN_EMAIL: "abc@d.c",
    CONF_LOGIN_PASSWORD: "passsword",
}

MOCK_OPTIONS_ALL = {
    CONF_SYSTEM_ID: 1234,
    CONF_LOGIN_EMAIL: "abc@d.c",
    CONF_LOGIN_PASSWORD: "passsword",
}

MOCK_CONFIG_ALL_V1 = {
    CONF_DEVICE_NAME: "Ferroamp Operation Settings",
    CONF_SYSTEM_ID: 1234,
    CONF_LOGIN_EMAIL: "abc@d.c",
    CONF_LOGIN_PASSWORD: "passsword",
}
