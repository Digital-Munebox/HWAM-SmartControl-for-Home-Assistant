"""Support for HWAM Smart Control binary sensors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    MAINTENANCE_THRESHOLD_HOURS,
)
from .coordinator import HWAMDataCoordinator
from .entity import HWAMEntity
from .models import StoveData

@dataclass
class HWAMBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing HWAM binary sensor entities."""
    
    is_on_fn: Callable[[StoveData], bool] | None = None
    attributes_fn: Callable[[StoveData], dict[str, Any]] | None = None
    alert_threshold: float | None = None
    critical_threshold: float | None = None

BINARY_SENSORS = (
    HWAMBinarySensorEntityDescription(
        key="door_open",
        name="Porte",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.state.door_open,
        attributes_fn=lambda data: {
            "last_opened": max(
                (h["timestamp"] for h in data.coordinator.temperature_history[-30:]
                if h.get("door_opened")),
                default=None
            ),
            "times_opened_today": sum(
                1 for h in data.coordinator.temperature_history[-288:]
                if h.get("door_opened")
            ) if len(data.coordinator.temperature_history) > 0 else 0,
        },
    ),
    HWAMBinarySensorEntityDescription(
        key="maintenance_needed",
        name="Maintenance nécessaire",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: (
            data.alarms.maintenance_alarms > 0 or
            (data.service_date.total_seconds() / 3600 > MAINTENANCE_THRESHOLD_HOURS)
        ),
        attributes_fn=lambda data: {
            "alarm_count": data.alarms.maintenance_alarms,
            "alarm_details": data.alarms.get_active_alarms(),
            "last_service": data.service_date.isoformat(),
            "hours_since_service": data.service_date.total_seconds() / 3600,
        },
    ),
    HWAMBinarySensorEntityDescription(
        key="safety_alarm",
        name="Alarme de sécurité",
        device_class=BinarySensorDeviceClass.SAFETY,
        is_on_fn=lambda data: data.alarms.safety_alarms > 0,
        attributes_fn=lambda data: {
            "alarm_count": data.alarms.safety_alarms,
            "alarm_details": data.alarms.get_active_alarms(),
            "temperature_critical": data.temperatures.stove_temperature > 500,
        },
        alert_threshold=400,  # Température d'alerte
        critical_threshold=500,  # Température critique
    ),
    HWAMBinarySensorEntityDescription(
        key="refill_needed",
        name="Rechargement nécessaire",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: data.alarms.refill_alarm,
        attributes_fn=lambda data: {
            "estimated_time_remaining": str(data.coordinator.predictions.get("refill_time")),
            "temperature_trend": data.coordinator.predictions.get("temperature_trend"),
            "efficiency_score": data.coordinator.predictions.get("efficiency_score"),
        },
    ),
    HWAMBinarySensorEntityDescription(
        key="optimal_performance",
        name="Performance optimale",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda data: (
            data.state.is_active and
            data.coordinator.predictions.get("efficiency_score", 0) > 80
        ),
        attributes_fn=lambda data: {
            "efficiency_score": data.coordinator.predictions.get("efficiency_score"),
            "temperature_stability": data.coordinator.predictions.get("temperature_trend"),
            "oxygen_level_optimal": 15 <= data.temperatures.oxygen_level <= 25,
        },
    ),
    HWAMBinarySensorEntityDescription(
        key="night_mode_active",
        name="Mode nuit actif",
        device_class=BinarySensorDeviceClass.POWER,
        is_on_fn=lambda data: data.state.night_lowering,
        attributes_fn=lambda data: {
            "start_time": data.night_begin_time.strftime("%H:%M"),
            "end_time": data.night_end_time.strftime("%H:%M"),
            "burn_level_reduced": data.state.burn_level < 3,
        },
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HWAM binary sensor based on a config entry."""
    coordinator: HWAMDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for description in BINARY_SENSORS:
        unique_id = f"{entry.entry_id}_{description.key}"
        entity = HWAMBinarySensor(
            coordinator=coordinator,
            entry_id=entry.entry_id,
            entity_description=description,
            unique_id=unique_id,
        )
        entities.append(entity)
    
    async_add_entities(entities)


class HWAMBinarySensor(HWAMEntity, BinarySensorEntity):
    """Representation of a HWAM binary sensor."""

    entity_description: HWAMBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: HWAMDataCoordinator,
        entry_id: str,
        entity_description: HWAMBinarySensorEntityDescription,
        unique_id: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry_id, entity_description)
        
        self._attr_unique_id = unique_id
        self._attr_name = f"{coordinator._name} {entity_description.name}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.coordinator.data is None or self.entity_description.is_on_fn is None:
            return None
            
        try:
            return self.entity_description.is_on_fn(self.coordinator.data)
        except Exception:
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = super().extra_state_attributes

        if self.coordinator.data is not None and self.entity_description.attributes_fn:
            try:
                attrs.update(self.entity_description.attributes_fn(self.coordinator.data))
            except Exception:
                pass

        # Ajout des seuils si définis
        if self.entity_description.alert_threshold is not None:
            attrs["alert_threshold"] = self.entity_description.alert_threshold
        if self.entity_description.critical_threshold is not None:
            attrs["critical_threshold"] = self.entity_description.critical_threshold

        # Diagnostic avancé
        if self.is_on:
            attrs["active_since"] = self.coordinator.last_update_dt
            if hasattr(self.coordinator.data, "temperatures"):
                attrs["temperature_at_activation"] = self.coordinator.data.temperatures.stove_temperature

        return attrs

    async def async_added_to_hass(self) -> None:
        """Gestion des notifications lors de l'ajout de l'entité."""
        await super().async_added_to_hass()

        # Création des notifications pour les alarmes de sécurité
        if (
            self.entity_description.key == "safety_alarm" 
            and self.is_on
            and self.coordinator.data is not None
        ):
            self.hass.components.persistent_notification.async_create(
                f"Alarme de sécurité sur le poêle {self._attr_name}: "
                f"{', '.join(self.coordinator.data.alarms.get_active_alarms())}",
                title="HWAM - Alarme de Sécurité",
                notification_id=f"hwam_safety_{self.unique_id}",
            )
