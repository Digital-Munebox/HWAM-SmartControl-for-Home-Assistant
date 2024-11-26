"""Tests for the HWAM Smart Control API."""
import pytest
from unittest.mock import AsyncMock, patch
from aiohttp import ClientError

from custom_components.hwam_stove.api import (
    HWAMApi,
    CannotConnect,
    InvalidResponse,
)

@pytest.fixture
def api():
    """Create a HWAM API instance."""
    return HWAMApi("192.168.1.100")

@pytest.mark.asyncio
async def test_get_stove_data(api):
    """Test getting stove data."""
    mock_data = {
        "stove_temperature": 12000,  # 120.00°C
        "room_temperature": 2100,    # 21.00°C
        "oxygen_level": 2000,        # 20.00%
        "phase": 3,
        "burn_level": 2,
        "operation_mode": 2,
        "door_open": 0,
        "updating": 0,
        "maintenance_alarms": 0,
        "safety_alarms": 0,
        "version_major": 1,
        "version_minor": 0,
        "version_build": 0,
        # ... autres données nécessaires
    }

    with patch("aiohttp.ClientSession.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value.__aenter__.return_value.status = 200
        mock_request.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_data
        )

        data = await api.get_stove_data()
        
        assert data.stove_temperature == 120.0
        assert data.room_temperature == 21.0
        assert data.oxygen_level == 20.0
        assert data.state.phase == 3
        assert data.state.burn_level == 2
        assert not data.state.door_open

@pytest.mark.asyncio
async def test_set_burn_level(api):
    """Test setting burn level."""
    with patch("aiohttp.ClientSession.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value.__aenter__.return_value.status = 200
        mock_request.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"response": "OK"}
        )

        assert await api.set_burn_level(3)

@pytest.mark.asyncio
async def test_connection_error(api):
    """Test API connection error."""
    with patch("aiohttp.ClientSession.request", side_effect=ClientError):
        with pytest.raises(CannotConnect):
            await api.get_stove_data()

@pytest.mark.asyncio
async def test_invalid_response(api):
    """Test invalid API response."""
    with patch("aiohttp.ClientSession.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value.__aenter__.return_value.status = 404

        with pytest.raises(InvalidResponse):
            await api.get_stove_data()
