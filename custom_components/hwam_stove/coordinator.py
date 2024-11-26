"""Data coordinator for HWAM integration."""
from datetime import datetime, timedelta
import logging
from typing import Any, Dict, List, Optional
import numpy as np
from collections import deque

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.util.dt import utcnow

from .api import HWAMApi, HWAMApiError
from .const import (
    DOMAIN, 
    DEFAULT_UPDATE_INTERVAL,
    TEMPERATURE_HISTORY_SIZE,
    MIN_SAMPLES_FOR_PREDICTION,
    PREDICTION_INTERVAL,
    MAINTENANCE_THRESHOLD_HOURS,
)
from .models import StoveData

_LOGGER = logging.getLogger(__name__)

class HWAMDataCoordinator(DataUpdateCoordinator[StoveData]):
    """Classe pour coordonner les mises à jour des données HWAM."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        api: HWAMApi, 
        name: str,
        update_interval: timedelta = DEFAULT_UPDATE_INTERVAL,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        
        self.api = api
        self._name = name
        self._last_update_success = True
        self._last_exception: Optional[Exception] = None
        
        # Historique des données
        self._temperature_history = deque(maxlen=TEMPERATURE_HISTORY_SIZE)
        self._oxygen_history = deque(maxlen=TEMPERATURE_HISTORY_SIZE)
        self._maintenance_check_time = None
        
        # Cache des prédictions
        self._last_prediction_time = None
        self._cached_predictions: Dict[str, Any] = {}

    async def _async_update_data(self) -> StoveData:
        """Mise à jour des données via l'API."""
        try:
            data = await self.api.get_stove_data()
            self._last_update_success = True
            
            # Mise à jour de l'historique
            timestamp = utcnow()
            self._update_history(data, timestamp)
            
            # Mise à jour des prédictions si nécessaire
            await self._update_predictions()
            
            # Vérification de la maintenance
            await self._check_maintenance(data)
            
            return data

        except HWAMApiError as err:
            self._last_update_success = False
            self._last_exception = err
            raise UpdateFailed(f"Erreur de communication avec l'API: {err}")

    def _update_history(self, data: StoveData, timestamp: datetime) -> None:
        """Met à jour l'historique des données."""
        self._temperature_history.append({
            "timestamp": timestamp,
            "stove_temp": data.temperatures.stove_temperature,
            "room_temp": data.temperatures.room_temperature
        })
        
        self._oxygen_history.append({
            "timestamp": timestamp,
            "level": data.temperatures.oxygen_level
        })

    async def _update_predictions(self) -> None:
        """Met à jour les prédictions si nécessaire."""
        now = utcnow()
        if (self._last_prediction_time is None or 
            now - self._last_prediction_time > PREDICTION_INTERVAL):
            
            self._cached_predictions = {
                "refill_time": self._predict_refill_time(),
                "temperature_trend": self._calculate_temperature_trend(),
                "efficiency_score": self._calculate_efficiency_score(),
            }
            self._last_prediction_time = now

    def _predict_refill_time(self) -> Optional[timedelta]:
        """Prédit le temps avant besoin de rechargement."""
        if len(self._temperature_history) < MIN_SAMPLES_FOR_PREDICTION:
            return None
            
        try:
            temps = [x["stove_temp"] for x in self._temperature_history]
            times = np.array(range(len(temps)))
            
            # Calcul de la tendance linéaire
            coeffs = np.polyfit(times, temps, 1)
            slope = coeffs[0]
            
            # Si la température baisse
            if slope < 0:
                current_temp = temps[-1]
                min_temp = 100  # Température minimum de fonctionnement
                time_to_min = (current_temp - min_temp) / abs(slope)
                return timedelta(minutes=int(time_to_min * 5))  # 5 minutes par échantillon
                
            return None
            
        except Exception as err:
            _LOGGER.warning("Erreur dans la prédiction de rechargement: %s", err)
            return None

    def _calculate_temperature_trend(self) -> str:
        """Calcule la tendance de température."""
        if len(self._temperature_history) < 3:
            return "stable"
            
        last_temps = [x["stove_temp"] for x in list(self._temperature_history)[-3:]]
        avg_change = (last_temps[-1] - last_temps[0]) / 2
        
        if avg_change > 5:
            return "rising"
        elif avg_change < -5:
            return "falling"
        return "stable"

    def _calculate_efficiency_score(self) -> Optional[float]:
        """Calcule un score d'efficacité basé sur la température et l'oxygène."""
        if len(self._temperature_history) < MIN_SAMPLES_FOR_PREDICTION:
            return None
            
        try:
            recent_temps = [x["stove_temp"] for x in list(self._temperature_history)[-5:]]
            recent_oxygen = [x["level"] for x in list(self._oxygen_history)[-5:]]
            
            temp_stability = 1 - (max(recent_temps) - min(recent_temps)) / max(recent_temps)
            oxygen_efficiency = 1 - (sum(recent_oxygen) / len(recent_oxygen)) / 100
            
            return (temp_stability * 0.6 + oxygen_efficiency * 0.4) * 100
            
        except Exception as err:
            _LOGGER.warning("Erreur dans le calcul du score d'efficacité: %s", err)
            return None

    async def _check_maintenance(self, data: StoveData) -> None:
        """Vérifie si une maintenance est nécessaire."""
        now = utcnow()
        if (not self._maintenance_check_time or 
            now - self._maintenance_check_time > timedelta(days=1)):
            
            try:
                service_age = now.date() - data.service_date
                if service_age.total_seconds() / 3600 > MAINTENANCE_THRESHOLD_HOURS:
                    self.hass.components.persistent_notification.async_create(
                        f"Votre poêle HWAM {self._name} a dépassé {MAINTENANCE_THRESHOLD_HOURS/24} "
                        "jours depuis sa dernière maintenance. Une révision est recommandée.",
                        title="Maintenance HWAM Recommandée",
                        notification_id=f"hwam_maintenance_{self._name}",
                    )
                
                self._maintenance_check_time = now
                
            except Exception as err:
                _LOGGER.warning("Erreur lors de la vérification de maintenance: %s", err)

    @property
    def temperature_history(self) -> List[Dict[str, Any]]:
        """Retourne l'historique des températures."""
        return list(self._temperature_history)

    @property
    def oxygen_history(self) -> List[Dict[str, Any]]:
        """Retourne l'historique des niveaux d'oxygène."""
        return list(self._oxygen_history)

    @property
    def predictions(self) -> Dict[str, Any]:
        """Retourne les dernières prédictions."""
        return self._cached_predictions.copy()

    async def set_burn_level(self, level: int) -> bool:
        """Définit le niveau de combustion."""
        try:
            result = await self.api.set_burn_level(level)
            if result:
                await self.async_refresh()
            return result
        except Exception as err:
            _LOGGER.error("Erreur lors du réglage du niveau de combustion: %s", err)
            raise

    async def start_combustion(self) -> bool:
        """Démarre la combustion."""
        try:
            result = await self.api.start_combustion()
            if result:
                await self.async_refresh()
            return result
        except Exception as err:
            _LOGGER.error("Erreur lors du démarrage de la combustion: %s", err)
            raise
