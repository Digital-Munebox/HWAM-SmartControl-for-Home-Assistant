"""Base entity for HWAM integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN, MANUFACTURER, MODEL
from ..coordinator import HWAMDataCoordinator
from ..models import StoveData

_LOGGER = logging.getLogger(__name__)

class HWAMEntity(CoordinatorEntity[HWAMDataCoordinator], Entity):
    """Base entity for HWAM integration."""

    _attr_has_entity_name = True

    def __init__(
        self, 
        coordinator: HWAMDataCoordinator, 
        entry_id: str,
        entity_description = None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        
        # Configuration entry ID
        self._entry_id = entry_id
        
        # Device unique identifiers
        self._device_unique_id = f"{DOMAIN}_{entry_id}"
        
        # Entity unique ID based on the device ID and entity type
        if entity_description is not None:
            self._attr_unique_id = f"{self._device_unique_id}_{entity_description.key}"
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_unique_id)},
            name=coordinator._name,
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=self.get_firmware_version(),
            suggested_area="Living Room",
            via_device=(DOMAIN, self._device_unique_id),
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return self._attr_unique_id

    # ... reste du code inchangé ...
