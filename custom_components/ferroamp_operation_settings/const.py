"""Constants file"""

from homeassistant.const import Platform
from homeassistant.const import __version__ as HA_VERSION

NAME = "Ferroamp Operation Settings"
DOMAIN = "ferroamp_operation_settings"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1.0"
ISSUE_URL = "https://github.com/jonasbkarlsson/ferroamp_operation_settings/issues"

# Icons
ICON = "mdi:flash"
ICON_SOLAR_POWER = "mdi:solar-power"
ICON_BATTERY_80 = "mdi:battery-80"
ICON_BATTERY_50 = "mdi:battery-50"
ICON_BATTERY_20 = "mdi:battery-20"
ICON_DOWNLOAD = "mdi:download"
ICON_UPDATE = "mdi:update"
ICON_INFORMATION = "mdi:information"

# Platforms
SWITCH = Platform.SWITCH
BUTTON = Platform.BUTTON
NUMBER = Platform.NUMBER
SELECT = Platform.SELECT
SENSOR = Platform.SENSOR
PLATFORMS = [SWITCH, BUTTON, NUMBER, SELECT, SENSOR]

# Entity names
ENTITY_NAME_MODE_SELECT = "Mode"
ENTITY_NAME_BATTERY_POWER_MODE_SELECT = "Battery power mode"
ENTITY_NAME_GET_DATA_BUTTON = "Get data"
ENTITY_NAME_UPDATE_BUTTON = "Update"
ENTITY_NAME_PV_SWITCH = "PV"
ENTITY_NAME_ACE_SWITCH = "ACE"
ENTITY_NAME_LIMIT_IMPORT_SWITCH = "Limit import"
ENTITY_NAME_LIMIT_EXPORT_SWITCH = "Limit export"
ENTITY_NAME_ACE_THRESHOLD_NUMBER = "ACE threshold"
ENTITY_NAME_DISCHARGE_THRESHOLD_NUMBER = "Discharge threshold"
ENTITY_NAME_CHARGE_THRESHOLD_NUMBER = "Charge threshold"
ENTITY_NAME_IMPORT_THRESHOLD_NUMBER = "Import threshold"
ENTITY_NAME_EXPORT_THRESHOLD_NUMBER = "Export threshold"
ENTITY_NAME_DISCHARGE_REFERENCE_NUMBER = "Discharge reference"
ENTITY_NAME_CHARGE_REFERENCE_NUMBER = "Charge reference"
ENTITY_NAME_LOWER_REFERENCE_NUMBER = "Lower reference"
ENTITY_NAME_UPPER_REFERENCE_NUMBER = "Upper reference"
ENTITY_NAME_STATUS_SENSOR = "Status"

MODE_DEFAULT = "Default"
MODE_PEAK_SHAVING = "Peak Shaving"
MODE_SELF_CONSUMPTION = "Self Consumption"

BATTERY_OFF = "Off"
BATTERY_CHARGE = "Charge"
BATTERY_DISCHARGE = "Discharge"

MODES = [MODE_DEFAULT, MODE_PEAK_SHAVING, MODE_SELF_CONSUMPTION]
BATTERY_POWER_MODES = [BATTERY_OFF, BATTERY_CHARGE, BATTERY_DISCHARGE]

STATUS_READY = "Ready"
STATUS_SUCCESS = "Success"
STATUS_FAILED = "Failed"

# Configuration and options
CONF_DEVICE_NAME = "device_name"
CONF_SYSTEM_ID = "system_id"
CONF_LOGIN_EMAIL = "login_email"
CONF_LOGIN_PASSWORD = "login_password"

# Defaults
DEFAULT_NAME = DOMAIN

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
Home Assistant: {HA_VERSION}
-------------------------------------------------------------------
"""
