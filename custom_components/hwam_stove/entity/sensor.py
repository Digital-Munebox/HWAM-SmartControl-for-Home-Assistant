"""Support for HWAM Smart Control sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    TEMP_CELSIUS,
    TIME_MINUTES,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_TIMESTAMP,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    DOMAIN,
    ICON_STOVE,
    ICON_TEMPERATURE,
    ICON_OXYGEN,
    ICON_VALVE,
    ICON_EFFICIENCY,
    PHASE_STATES,
    OPERATION_MODES,
)
from .coordinator import HWAMDataCoordinator
from .entity import HWAMEntity
from .models import StoveData

@dataclass
class HWAMSensorEntityDescription(SensorEntityDescription):
    """Class describing HWAM sensor entities."""

    value_fn: Callable[[StoveData], StateType] | None = None
    attributes_fn: Callable[[StoveData], dict[str, Any]] | None = None

SENSORS: tuple[HWAMSensorEntityDescription, ...] = (
    HWAMSensorEntityDescription(
        key="stove_temperature",
        name="Température du poêle",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_TEMPERATURE,
        value_fn=lambda data: data.temperatures.stove_temperature,
        attributes_fn=lambda data: {
            "trend": data.coordinator.predictions.get("temperature_trend", "unknown"),
            "min_24h": min(h["stove_temp"] for h in data.coordinator.temperature_history[-288:]) if len(data.coordinator.temperature_history) >= 288 else None,
            "max_24h": max(h["stove_temp"] for h in data.coordinator.temperature_history[-288:]) if len(data.coordinator.temperature_history) >= 288 else None,
        },
    ),
    HWAMSensorEntityDescription(
        key="room_temperature",
        name="Température ambiante",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_TEMPERATURE,
        value_fn=lambda data: data.temperatures.room_temperature,
        attributes_fn=lambda data: {
            "min_24h": min(h["room_temp"] for h in data.coordinator.temperature_history[-288:]) if len(data.coordinator.temperature_history) >= 288 else None,
            "max_24h": max(h["room_temp"] for h in data.coordinator.temperature_history[-288:]) if len(data.coordinator.temperature_history) >= 288 else None,
        },
    ),
    HWAMSensorEntityDescription(
        key="oxygen_level",
        name="Niveau d'oxygène",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_OXYGEN,
        value_fn=lambda data: data.temperatures.oxygen_level,
        attributes_fn=lambda data: {
            "average": sum(h["level"] for h in data.coordinator.oxygen_history[-5:]) / 5 if len(data.coordinator.oxygen_history) >= 5 else None,
        },
    ),
    HWAMSensorEntityDescription(
        key="efficiency_score",
        name="Score d'efficacité",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon=ICON_EFFICIENCY,
        value_fn=lambda data: data.coordinator.predictions.get("efficiency_score"),
        attributes_fn=lambda data: {
            "temperature_stability": data.coordinator.predictions.get("temperature_trend"),
            "oxygen_efficiency": sum(h["level"] for h in data.coordinator.oxygen_history[-5:]) / 5 if len(data.coordinator.oxygen_history) >= 5 else None,
        },
    ),
    HWAMSensorEntityDescription(
        key="burn_phase",
        name="Phase de combustion",
        icon=ICON_STOVE,
        value_fn=lambda data: PHASE_STATES.get(data.state.phase, "Unknown"),
        attributes_fn=lambda data: {
            "phase_number": data.state.phase,
            "is_active": data.state.is_active,
            "estimated_refill_time": str(data.coordinator.predictions.get("refill_time")) if data.coordinator.predictions.get("refill_time") else None,
        },
    ),
    HWAMSensorEntityDescription(
        key="operation_mode",
        name="Mode de fonctionnement",
        icon=ICON_STOVE,
        value_fn=lambda data: OPERATION_MODES.get(data.state.operation_mode, "Unknown"),
        attributes_fn=lambda data: {
            "mode_number": data.state.operation_mode,
            "night_mode": data.state.night_lowering,
            "updating": data.state.updating,
        },
    ),
    HWAMSensorEntityDescription(
        key="valve1",
        name="Valve 1",
        native_unit_of_measurement=PERCENTAGE,
        icon=ICON_VALVE,
        value_fn=lambda data: data.valve1_position,
    ),
    HWAMSensorEntityDescription(
        key="valve2",
        name="Valve 2",
        native_unit_of_measurement=PERCENTAGE,
        icon=ICON_VALVE,
        value_fn=lambda data: data.valve2_position,
    ),
    HWAMSensorEntityDescription(
        key="valve3",
        name="Valve 3",
        native_unit_of_measurement=PERCENTAGE,
        icon=ICON_VALVE,
        value_fn=lambda data: data.valve3_position,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HWAM sensor based on a config entry."""
    coordinator: HWAMDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for description in SENSORS:
        unique_id = f"{entry.entry_id}_{description.key}"
        entity = HWAMSensor(
            coordinator=coordinator,
            entry_id=entry.entry_id,
            entity_description=description,
            unique_id=unique_id,
        )
        entities.append(entity)
    
    async_add_entities(entities)


class HWAMSensor(HWAMEntity, SensorEntity):
    """Representation of a HWAM sensor."""

    entity_description: HWAMSensorEntityDescription

    def __init__(
        self,
        coordinator: HWAMDataCoordinator,
        entry_id: str,
        entity_description: HWAMSensorEntityDescription,
        unique_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, entity_description)
        
        self._attr_unique_id = unique_id
        self._attr_name = f"{coordinator._name} {entity_description.name}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
            
        if self.entity_description.value_fn is None:
            return None
            
        try:
            return self.entity_description.value_fn(self.coordinator.data)
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

        # Add diagnostic attributes
        attrs.update({
            "last_update": self.coordinator.last_update_success,
            "last_update_time": self.coordinator.last_update_dt,
            "firmware_version": self.coordinator.data.firmware_version if self.coordinator.data else None,
            "algorithm": self.coordinator.data.algorithm if self.coordinator.data else None,
        })

        return attrs
