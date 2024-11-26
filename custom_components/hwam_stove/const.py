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

# Services disponibles
SERVICE_SET_BURN_LEVEL = "set_burn_level"  # Contrôle du niveau de combustion
SERVICE_START_COMBUSTION = "start_combustion"  # Démarrage de la combustion
SERVICE_SET_NIGHT_MODE = "set_night_mode"  # Configuration du mode nuit

# Attributs
ATTR_BURN_LEVEL = "burn_level"
ATTR_PHASE = "phase"
ATTR_OPERATION_MODE = "operation_mode"
ATTR_FIRMWARE_VERSION = "firmware_version"
ATTR_WIFI_VERSION = "wifi_version"
ATTR_REMOTE_VERSION = "remote_version"
ATTR_ALGORITHM = "algorithm"

# États documentés du poêle
PHASE_STATES = {
    1: "Allumage",      # Phase d'allumage initiale
    2: "Démarrage",     # Phase de démarrage
    3: "Combustion",    # Phase de combustion principale
    4: "Braises",       # Phase de braises
    5: "Veille"         # Mode veille
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

# Points de terminaison API
ENDPOINT_GET_STOVE_DATA = "/get_stove_data"  # Lecture des données
ENDPOINT_START = "/start"  # Démarrage
ENDPOINT_SET_BURN_LEVEL = "/set_burn_level"  # Niveau de combustion
ENDPOINT_SET_NIGHT_TIME = "/set_night_time"  # Mode nuit

# Unités de mesure
TEMP_CELSIUS = "°C"
PERCENTAGE = "%"

# Icônes
ICON_STOVE = "mdi:fireplace"
ICON_TEMPERATURE = "mdi:thermometer"
ICON_OXYGEN = "mdi:molecule"
ICON_VALVE = "mdi:valve"
ICON_TIMER = "mdi:timer"
ICON_ALERT = "mdi:alert"
ICON_MAINTENANCE = "mdi:tools"

# Messages d'erreur
ERROR_CANNOT_CONNECT = "cannot_connect"
ERROR_INVALID_AUTH = "invalid_auth"
ERROR_UNKNOWN = "unknown"

# Catégories d'entités
ENTITY_CATEGORY_CONFIG = "config"
ENTITY_CATEGORY_DIAGNOSTIC = "diagnostic"

# Seuils et limites
MIN_BURN_LEVEL = 0  # Niveau minimum de combustion
MAX_BURN_LEVEL = 5  # Niveau maximum de combustion
MIN_UPDATE_INTERVAL = 10  # Intervalle minimum de mise à jour en secondes
MAX_TEMP_WARNING = 500  # Température d'avertissement en °C
MIN_OXYGEN_WARNING = 15  # Niveau d'oxygène minimum en %

# Zones suggérées
SUGGESTED_AREA = "Living Room"

# Historique
TEMPERATURE_HISTORY_SIZE = 288  # 24h avec mise à jour toutes les 5 minutes
