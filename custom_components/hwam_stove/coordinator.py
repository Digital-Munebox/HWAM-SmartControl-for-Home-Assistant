"""Data coordinator for HWAM integration."""
from datetime import datetime, timedelta
import logging
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import HWAMApi, HWAMApiError
from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL
from .models import StoveData

_LOGGER = logging.getLogger(__name__)

class HWAMDataCoordinator(DataUpdateCoordinator[StoveData]):
    """Class to manage fetching data from HWAM stove."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        api: HWAMApi, 
        name: str,
        update_interval: timedelta = DEFAULT_UPDATE_INTERVAL,
    ) -> None:
        """Initialize."""
        self.api = api
        self._name = name
        self._last_update_success = True
        self._last_exception: Optional[Exception] = None
        
        # Historique des données
        self._temperature_history: list[Dict[str, Any]] = []
        self._oxygen_history: list[Dict[str, Any]] = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> StoveData:
        """Update data via library."""
        try:
            data = await self.api.get_stove_data()
            self._last_update_success = True
            
            # Mise à jour de l'historique
            timestamp = datetime.now()
            self._temperature_history.append({
                "timestamp": timestamp,
                "stove_temp": data.stove_temperature,
                "room_temp": data.room_temperature
            })
            self._oxygen_history.append({
                "timestamp": timestamp,
                "level": data.oxygen_level
            })
            
            # Limite la taille de l'historique
            max_history = 100
            if len(self._temperature_history) > max_history:
                self._temperature_history = self._temperature_history[-max_history:]
            if len(self._oxygen_history) > max_history:
                self._oxygen_history = self._oxygen_history[-max_history:]
                
            # Vérification des alarmes
            if data.alarms.has_alarms():
                active_alarms = data.alarms.get_active_alarms()
                for alarm in active_alarms:
                    _LOGGER.warning(
                        "Alarme active sur %s: %s", 
                        self._name, 
                        alarm
                    )
                    
                    # Création d'une notification persistante
                    self.hass.components.persistent_notification.async_create(
                        f"Alarme sur votre poêle HWAM: {alarm}",
                        title="HWAM Alarme",
                        notification_id=f"hwam_alarm_{self._name}"
                    )

            return data

        except HWAMApiError as err:
            self._last_update_success = False
            self._last_exception = err
            raise UpdateFailed(f"Error communicating with API: {err}")
            
    @property
    def last_update_success(self) -> bool:
        """Return if last update was successful."""
        return self._last_update_success

    @property
    def last_exception(self) -> Optional[Exception]:
        """Return last update exception."""
        return self._last_exception

    @property
    def temperature_history(self) -> list[Dict[str, Any]]:
        """Return temperature history."""
        return self._temperature_history

    @property
    def oxygen_history(self) -> list[Dict[str, Any]]:
        """Return oxygen history."""
        return self._oxygen_history

    async def set_burn_level(self, level: int) -> bool:
        """Set burn level."""
        try:
            result = await self.api.set_burn_level(level)
            if result:
                await self.async_refresh()
            return result
        except Exception as err:
            _LOGGER.error("Error setting burn level: %s", err)
            raise

    async def start_combustion(self) -> bool:
        """Start combustion."""
        try:
            result = await self.api.start_combustion()
            if result:
                await self.async_refresh()
            return result
        except Exception as err:
            _LOGGER.error("Error starting combustion: %s", err)
            raise
