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

from .const import DOMAIN
from .coordinator import HWAMDataCoordinator
from .entity import HWAMEntity
from .models import StoveData

@dataclass
class HWAMBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing HWAM binary sensor entities."""

    is_on_fn: Callable[[StoveData], bool] | None = None

BINARY_SENSORS = (
    HWAMBinarySensorEntityDescription(
        key="door_open",
        name="Porte",
        device_class=BinarySensorDeviceClass.DOOR,
        is_on_fn=lambda data: data.state.door_open,
    ),
    HWAMBinarySensorEntityDescription(
        key="maintenance_needed",
        name="Maintenance nécessaire",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: data.alarms.maintenance_alarms > 0,
    ),
    HWAMBinarySensorEntityDescription(
        key="safety_alarm",
        name="Alarme de sécurité",
        device_class=BinarySensorDeviceClass.SAFETY,
        is_on_fn=lambda data: data.alarms.safety_alarms > 0,
    ),
    HWAMBinarySensorEntityDescription(
        key="refill_needed",
        name="Rechargement nécessaire",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: data.alarms.refill_alarm,
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
        unique_id = f"{entry.unique_id}_{description.key}"
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
        
        # Ensure unique ID is properly set
        self._attr_unique_id = unique_id
        
        # Set name based on entity description
        self._attr_name = f"{coordinator._name} {entity_description.name}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.entity_description.is_on_fn is None:
            return None
            
        try:
            return self.entity_description.is_on_fn(self.coordinator.data)
        except Exception:
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = super().extra_state_attributes
        
        # Add specific attributes for each sensor type
        if self.entity_description.key == "maintenance_needed":
            attrs["alarm_count"] = self.coordinator.data.alarms.maintenance_alarms
        elif self.entity_description.key == "safety_alarm":
            attrs["alarm_count"] = self.coordinator.data.alarms.safety_alarms
            
        return attrs
