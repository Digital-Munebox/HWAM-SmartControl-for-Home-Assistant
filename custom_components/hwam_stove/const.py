"""Constants for the HWAM Smart Control integration."""
from datetime import timedelta
from typing import Final

DOMAIN: Final = "hwam_stove"
MANUFACTURER: Final = "HWAM"
MODEL: Final = "Smart Control"

# Configuration
CONF_HOST = "host"
CONF_NAME = "name"
DEFAULT_NAME = "HWAM Stove"
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=30)

# Services
SERVICE_SET_BURN_LEVEL = "set_burn_level"
SERVICE_START_COMBUSTION = "start_combustion"
SERVICE_SET_NIGHT_MODE = "set_night_mode"

# Attributes
ATTR_BURN_LEVEL = "burn_level"
ATTR_PHASE = "phase"
ATTR_OPERATION_MODE = "operation_mode"
ATTR_FIRMWARE_VERSION = "firmware_version"
ATTR_WIFI_VERSION = "wifi_version"
ATTR_REMOTE_VERSION = "remote_version"
ATTR_ALGORITHM = "algorithm"

# States
PHASE_STATES = {
    1: "Allumage",
    2: "Démarrage",
    3: "Combustion",
    4: "Braises",
    5: "Veille"
}

OPERATION_MODES = {
    0: "Initialisation",
    1: "Auto-test",
    2: "Normal",
    3: "Défaut température",
    4: "Défaut O2",
    5: "Calibration",
    6: "Sécurité",
    7: "Manuel",
    8: "Test moteur",
    9: "Combustion lente",
    10: "Tension faible"
}

# Endpoints
ENDPOINT_GET_STOVE_DATA = "/get_stove_data"
ENDPOINT_START = "/start"
ENDPOINT_SET_BURN_LEVEL = "/set_burn_level"
ENDPOINT_SET_NIGHT_TIME = "/set_night_time"

# Units
TEMP_CELSIUS = "°C"
PERCENTAGE = "%"

# Icons
ICON_STOVE = "mdi:fireplace"
ICON_TEMPERATURE = "mdi:thermometer"
ICON_OXYGEN = "mdi:molecule"
ICON_VALVE = "mdi:valve"
ICON_TIMER = "mdi:timer"
ICON_ALERT = "mdi:alert"
ICON_MAINTENANCE = "mdi:tools"

# Error messages
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_AUTH = "invalid_auth"
ERROR_UNKNOWN = "unknown"

# Entity Categories
ENTITY_CATEGORY_CONFIG = "config"
ENTITY_CATEGORY_DIAGNOSTIC = "diagnostic"

# Suggested Areas
SUGGESTED_AREA = "Living Room"
