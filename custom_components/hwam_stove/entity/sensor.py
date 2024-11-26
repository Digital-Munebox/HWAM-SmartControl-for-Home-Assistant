"""Support for HWAM Smart Control sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
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

from .const import (
    DOMAIN,
    ICON_STOVE,
    ICON_TEMPERATURE,
    ICON_OXYGEN,
    ICON_VALVE,
    PHASE_STATES,
    OPERATION_MODES,
)
from .coordinator import HWAMDataCoordinator
from .entity import HWAMEntity
from .models import StoveData

@dataclass
class HWAMSensorEntityDescription(SensorEntityDescription):
    """Class describing HWAM sensor entities."""

    value_fn: Callable[[StoveData], Any] | None = None

# ... SENSORS definition reste inchangée ...

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HWAM sensor based on a config entry."""
    coordinator: HWAMDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create entities with proper unique IDs
    entities = []
    for description in SENSORS:
        unique_id = f"{entry.unique_id}_{description.key}"
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
        
        # Ensure unique ID is properly set
        self._attr_unique_id = unique_id
        
        # Set name based on entity description
        self._attr_name = f"{coordinator._name} {entity_description.name}"

    # ... reste du code inchangé ...
