"""Global fixtures for HWAM integration tests."""
import pytest

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from custom_components.hwam_stove.const import DOMAIN

@pytest.fixture
def mock_setup_entry() -> None:
    """Fixture to mock setting up an entry."""
    pass

@pytest.fixture
async def mock_integration(hass: HomeAssistant) -> None:
    """Set up the HWAM integration."""
    assert await async_setup_component(hass, DOMAIN, {
        DOMAIN: {
            "host": "192.168.1.100",
            "name": "Test Stove"
        }
    })
    await hass.async_block_till_done()

@pytest.fixture
def mock_stove_data():
    """Fixture with mock stove data."""
    return {
        "stove_temperature": 24500,  # 245°C
        "room_temperature": 2100,    # 21°C
        "oxygen_level": 2000,        # 20%
        "phase": 3,
        "burn_level": 2,
        "operation_mode": 2,
        "door_open": 0,
        "valve1_position": 50,
        "valve2_position": 60,
        "valve3_position": 70,
        "maintenance_alarms": 0,
        "safety_alarms": 0,
        "version_major": 1,
        "version_minor": 0,
        "version_build": 0,
        "algorithm": "IHS"
    }
