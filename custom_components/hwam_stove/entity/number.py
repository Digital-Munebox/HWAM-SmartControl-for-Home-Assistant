"""Support for HWAM Smart Control number entities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    ICON_STOVE,
)
from .coordinator import HWAMDataCoordinator
from .entity import HWAMEntity

@dataclass
class HWAMNumberEntityDescription(NumberEntityDescription):
    """Class describing HWAM number entities."""

    # Si besoin d'attributs supplémentaires
    pass

NUMBER_TYPES = (
    HWAMNumberEntityDescription(
        key="burn_level",
        name="Niveau de combustion",
        icon=ICON_STOVE,
        native_min_value=0,
        native_max_value=5,
        native_step=1,
        mode=NumberMode.SLIDER,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HWAM number entities based on a config entry."""
    coordinator: HWAMDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for description in NUMBER_TYPES:
        # Création d'un unique_id basé sur l'entrée de configuration et la clé de l'entité
        unique_id = f"{entry.unique_id}_{description.key}"
        entity = HWAMNumber(
            coordinator=coordinator,
            entry_id=entry.entry_id,
            entity_description=description,
            unique_id=unique_id,
        )
        entities.append(entity)
    
    async_add_entities(entities)


class HWAMNumber(HWAMEntity, NumberEntity):
    """Representation of a HWAM number entity."""

    entity_description: HWAMNumberEntityDescription

    def __init__(
        self,
        coordinator: HWAMDataCoordinator,
        entry_id: str,
        entity_description: HWAMNumberEntityDescription,
        unique_id: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, entry_id, entity_description)
        
        self._attr_unique_id = unique_id
        self._attr_name = f"{coordinator._name} {entity_description.name}"

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        try:
            return float(self.coordinator.data.state.burn_level)
        except (AttributeError, TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await self.coordinator.api.set_burn_level(int(value))
        await self.coordinator.async_refresh()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        attrs = super().extra_state_attributes
        
        try:
            # Ajout d'attributs spécifiques au niveau de combustion
            attrs.update({
                "phase_actuelle": self.coordinator.data.state.phase,
                "mode_operation": self.coordinator.data.state.operation_mode,
                "temperature_poele": self.coordinator.data.stove_temperature,
            })
        except AttributeError:
            pass
            
        return attrs
