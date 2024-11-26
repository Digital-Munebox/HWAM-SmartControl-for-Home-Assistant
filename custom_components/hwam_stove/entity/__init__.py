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
        device_id: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._device_id = device_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=coordinator._name,
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=self.get_firmware_version(),
            suggested_area="Living Room",
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    @property
    def stove_data(self) -> StoveData:
        """Get current stove data."""
        return self.coordinator.data

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success 
            and super().available
        )

    def get_firmware_version(self) -> str:
        """Get firmware version."""
        try:
            return self.coordinator.data.firmware_version
        except AttributeError:
            return "Unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        try:
            return {
                "last_update_success": self.coordinator.last_update_success,
                "last_exception": str(self.coordinator.last_exception) if self.coordinator.last_exception else None,
                "algorithm": self.coordinator.data.algorithm,
                "wifi_version": self.coordinator.data.wifi_version,
                "remote_version": self.coordinator.data.remote_version,
            }
        except AttributeError:
            return {}
