"""The HWAM Smart Control integration."""
import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, SERVICE_SET_BURN_LEVEL, SERVICE_START_COMBUSTION, SERVICE_SET_NIGHT_MODE
from .coordinator import HWAMDataCoordinator
from .api import HWAMApi

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the HWAM Smart Control integration."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HWAM Smart Control from a config entry."""
    host = entry.data[CONF_HOST]
    
    # Initialisation de l'API
    api = HWAMApi(host)
    
    # Initialisation du coordinateur
    coordinator = HWAMDataCoordinator(
        hass=hass,
        api=api,
        name=entry.title,
    )
    
    # Première mise à jour des données
    await coordinator.async_config_entry_first_refresh()
    
    # Stockage du coordinateur pour utilisation par les plateformes
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Configuration des services
    async def handle_start_combustion(call: ServiceCall) -> None:
        """Handle the start combustion service call."""
        coordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.api.start_combustion()
        await coordinator.async_refresh()

    async def handle_set_burn_level(call: ServiceCall) -> None:
        """Handle the set burn level service call."""
        coordinator = hass.data[DOMAIN][entry.entry_id]
        level = call.data["level"]
        await coordinator.api.set_burn_level(level)
        await coordinator.async_refresh()

    async def handle_set_night_mode(call: ServiceCall) -> None:
        """Handle the set night mode service call."""
        coordinator = hass.data[DOMAIN][entry.entry_id]
        start_time = call.data["start_time"]
        end_time = call.data["end_time"]
        await coordinator.api.set_night_time(start_time, end_time)
        await coordinator.async_refresh()

    # Enregistrement des services
    hass.services.async_register(
        DOMAIN,
        SERVICE_START_COMBUSTION,
        handle_start_combustion,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_BURN_LEVEL,
        handle_set_burn_level,
        schema=vol.Schema({
            vol.Required("level"): vol.All(
                vol.Coerce(int),
                vol.Range(min=0, max=5)
            )
        })
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_NIGHT_MODE,
        handle_set_night_mode,
        schema=vol.Schema({
            vol.Required("start_time"): cv.time,
            vol.Required("end_time"): cv.time
        })
    )
    
    # Configuration des plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Déchargement des plateformes
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Désenregistrement des services
        for service in [SERVICE_START_COMBUSTION, SERVICE_SET_BURN_LEVEL, SERVICE_SET_NIGHT_MODE]:
            if hass.services.has_service(DOMAIN, service):
                hass.services.async_remove(DOMAIN, service)
        
        # Nettoyage des données
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.api.close()

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
