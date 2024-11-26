"""Support for HWAM Smart Control number entities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
    NumberDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    ICON_STOVE,
    MIN_BURN_LEVEL,
    MAX_BURN_LEVEL,
    STEP_BURN_LEVEL,
)
from .coordinator import HWAMDataCoordinator
from .entity import HWAMEntity
from .models import StoveData

@dataclass
class HWAMNumberEntityDescription(NumberEntityDescription):
    """Class describing HWAM number entities."""

    value_fn: Callable[[StoveData], float] | None = None
    set_fn: Callable[[HWAMDataCoordinator, float], Any] | None = None
    attributes_fn: Callable[[StoveData], dict[str, Any]] | None = None

NUMBER_TYPES = (
    HWAMNumberEntityDescription(
        key="burn_level",
        name="Niveau de combustion",
        icon=ICON_STOVE,
        native_min_value=MIN_BURN_LEVEL,
        native_max_value=MAX_BURN_LEVEL,
        native_step=STEP_BURN_LEVEL,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement="niveau",
        value_fn=lambda data: float(data.state.burn_level),
        set_fn=lambda coordinator, value: coordinator.set_burn_level(int(value)),
        attributes_fn=lambda data: {
            "phase_actuelle": data.state.phase,
            "mode_operation": data.state.operation_mode,
            "temperature_actuelle": data.temperatures.stove_temperature,
            "efficacite": data.coordinator.predictions.get("efficiency_score"),
            "tendance_temperature": data.coordinator.predictions.get("temperature_trend"),
            "temps_avant_rechargement": str(data.coordinator.predictions.get("refill_time", "N/A")),
            "mode_nuit_actif": data.state.night_lowering,
            "niveau_recommande": _get_recommended_burn_level(data),
        },
    ),
)

def _get_recommended_burn_level(data: StoveData) -> int:
    """Calcule le niveau de combustion recommandé basé sur différents facteurs."""
    if not data.state.is_active:
        return 0
        
    # Facteurs de décision
    current_temp = data.temperatures.stove_temperature
    room_temp = data.temperatures.room_temperature
    oxygen_level = data.temperatures.oxygen_level
    temp_trend = data.coordinator.predictions.get("temperature_trend")
    
    # Logique de recommandation
    if current_temp > 500:  # Température trop haute
        return max(MIN_BURN_LEVEL, data.state.burn_level - 1)
    elif current_temp < 200 and room_temp < 19:  # Besoin de chaleur
        return min(MAX_BURN_LEVEL, data.state.burn_level + 1)
    elif temp_trend == "falling" and room_temp < 20:
        return min(MAX_BURN_LEVEL, data.state.burn_level + 1)
    elif temp_trend == "rising" and current_temp > 400:
        return max(MIN_BURN_LEVEL, data.state.burn_level - 1)
    
    # Mode par défaut
    return data.state.burn_level

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HWAM number entities based on a config entry."""
    coordinator: HWAMDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for description in NUMBER_TYPES:
        unique_id = f"{entry.entry_id}_{description.key}"
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
        if self.coordinator.data is None or self.entity_description.value_fn is None:
            return None
            
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except Exception:
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if self.entity_description.set_fn is None:
            return

        try:
            await self.entity_description.set_fn(self.coordinator, value)
            self.async_write_ha_state()
            
            # Notification si le niveau est très différent de la recommandation
            if self.entity_description.key == "burn_level":
                recommended = _get_recommended_burn_level(self.coordinator.data)
                if abs(value - recommended) >= 2:
                    self.hass.components.persistent_notification.async_create(
                        f"Le niveau de combustion défini ({value}) est très différent "
                        f"du niveau recommandé ({recommended}). Cela pourrait affecter "
                        "l'efficacité de la combustion.",
                        title="HWAM - Recommandation",
                        notification_id=f"hwam_burn_level_{self.unique_id}",
                    )
                    
        except Exception as err:
            _LOGGER.error("Erreur lors de la définition de la valeur: %s", err)
            raise

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = super().extra_state_attributes

        if self.coordinator.data is not None and self.entity_description.attributes_fn:
            try:
                attrs.update(self.entity_description.attributes_fn(self.coordinator.data))
            except Exception:
                pass

        return attrs

    async def async_added_to_hass(self) -> None:
        """Configure des notifications au démarrage."""
        await super().async_added_to_hass()

        if (
            self.entity_description.key == "burn_level" 
            and self.coordinator.data is not None
        ):
            recommended = _get_recommended_burn_level(self.coordinator.data)
            current = self.native_value
            if current is not None and abs(current - recommended) >= 2:
                self.hass.components.persistent_notification.async_create(
                    f"Le niveau de combustion actuel ({current}) est très différent "
                    f"du niveau recommandé ({recommended}). Considérez un ajustement "
                    "pour optimiser la combustion.",
                    title="HWAM - Recommandation initiale",
                    notification_id=f"hwam_burn_level_init_{self.unique_id}",
                )
