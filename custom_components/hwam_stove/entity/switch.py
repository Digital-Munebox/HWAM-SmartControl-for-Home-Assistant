"""Support for HWAM Smart Control switches."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HWAMDataCoordinator
from .entity import HWAMEntity
from .models import StoveData

@dataclass
class HWAMSwitchEntityDescription(SwitchEntityDescription):
    """Class describing HWAM switch entities."""
    
    is_on_fn: Callable[[StoveData], bool] = None
    turn_on_fn: Callable[["HWAMSwitch"], None] = None
    turn_off_fn: Callable[["HWAMSwitch"], None] = None

SWITCH_TYPES = (
    HWAMSwitchEntityDescription(
        key="night_mode",
        name="Mode nuit",
        icon="mdi:weather-night",
        is_on_fn=lambda data: data.state.night_lowering,
    ),
    HWAMSwitchEntityDescription(
        key="remote_refill_alarm",
        name="Alarme de rechargement à distance",
        icon="mdi:bell-ring",
        is_on_fn=lambda data: data.alarms.remote_refill_alarm,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HWAM switch entities based on a config entry."""
    coordinator: HWAMDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for description in SWITCH_TYPES:
        # Création d'un unique_id basé sur l'entrée de configuration et la clé de l'entité
        unique_id = f"{entry.unique_id}_{description.key}"
        entity = HWAMSwitch(
            coordinator=coordinator,
            entry_id=entry.entry_id,
            entity_description=description,
            unique_id=unique_id,
        )
        entities.append(entity)
    
    async_add_entities(entities)


class HWAMSwitch(HWAMEntity, SwitchEntity):
    """Representation of a HWAM switch entity."""

    entity_description: HWAMSwitchEntityDescription

    def __init__(
        self,
        coordinator: HWAMDataCoordinator,
        entry_id: str,
        entity_description: HWAMSwitchEntityDescription,
        unique_id: str,
    ) -> None:
        """Initialize the switch entity."""
        super().__init__(coordinator, entry_id, entity_description)
        
        self._attr_unique_id = unique_id
        self._attr_name = f"{coordinator._name} {entity_description.name}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.entity_description.is_on_fn is None:
            return None
            
        try:
            return self.entity_description.is_on_fn(self.coordinator.data)
        except Exception:
            return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        if self.entity_description.key == "night_mode":
            await self.coordinator.api.set_night_time(True)
        elif self.entity_description.key == "remote_refill_alarm":
            await self.coordinator.api.set_remote_refill_alarm(True)
            
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        if self.entity_description.key == "night_mode":
            await self.coordinator.api.set_night_time(False)
        elif self.entity_description.key == "remote_refill_alarm":
            await self.coordinator.api.set_remote_refill_alarm(False)
            
        await self.coordinator.async_refresh()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        attrs = super().extra_state_attributes
        
        if self.entity_description.key == "night_mode":
            try:
                attrs.update({
                    "heure_debut": self.coordinator.data.night_begin_time.isoformat(),
                    "heure_fin": self.coordinator.data.night_end_time.isoformat(),
                })
            except AttributeError:
                pass
                
        return attrs
