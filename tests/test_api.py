"""Test the HWAM API."""
import pytest
from unittest.mock import patch, AsyncMock
from aiohttp import ClientError

from custom_components.hwam_stove.api import (
    HWAMApi,
    CannotConnect,
    InvalidResponse
)

@pytest.fixture
def api():
    """Create a HWAM API object."""
    return HWAMApi("192.168.1.100")

@pytest.mark.asyncio
async def test_get_stove_data(api, mock_stove_data):
    """Test getting stove data."""
    with patch("aiohttp.ClientSession.request", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_stove_data
        )

        data = await api.get_stove_data()
        assert data.temperatures.stove_temperature == 245.0
        assert data.temperatures.room_temperature == 21.0
        assert data.temperatures.oxygen_level == 20.0
        assert data.state.phase == 3
        assert data.state.burn_level == 2

@pytest.mark.asyncio
async def test_connection_error(api):
    """Test API when connection fails."""
    with patch("aiohttp.ClientSession.request", side_effect=ClientError):
        with pytest.raises(CannotConnect):
            await api.get_stove_data()

@pytest.mark.asyncio
async def test_invalid_response(api):
    """Test API when receiving invalid response."""
    with patch("aiohttp.ClientSession.request", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 404
        with pytest.raises(InvalidResponse):
            await api.get_stove_data()
