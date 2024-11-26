"""HWAM Smart Control API Client."""
from datetime import datetime
import logging
from typing import Optional

import aiohttp
import async_timeout

from .const import (
    ENDPOINT_GET_STOVE_DATA,
    ENDPOINT_SET_BURN_LEVEL,
    ENDPOINT_START,
    ENDPOINT_SET_NIGHT_TIME,
)
from .models import StoveData

_LOGGER = logging.getLogger(__name__)

class HWAMApiError(Exception):
    """Exception for HWAM API errors."""
    pass

class CannotConnect(HWAMApiError):
    """Error to indicate we cannot connect."""
    pass

class InvalidResponse(HWAMApiError):
    """Error to indicate invalid response from API."""
    pass

class HWAMApi:
    """HWAM Smart Control API client."""

    def __init__(
        self, 
        host: str, 
        session: Optional[aiohttp.ClientSession] = None,
        request_timeout: int = 10
    ) -> None:
        """Initialize the API client."""
        self._host = host
        self._session = session
        self._request_timeout = request_timeout
        self._base_url = f"http://{host}"
        self._close_session = False

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True
        return self._session

    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[dict] = None, 
        data: Optional[dict] = None
    ) -> dict:
        """Make request to API."""
        session = await self._get_session()
        url = f"{self._base_url}{endpoint}"

        try:
            async with async_timeout.timeout(self._request_timeout):
                _LOGGER.debug("Making request to %s", url)
                async with session.request(
                    method, 
                    url, 
                    params=params, 
                    json=data,
                    headers={"Accept": "application/json"}
                ) as response:
                    if response.status != 200:
                        raise InvalidResponse(
                            f"Invalid response from API: {response.status}"
                        )
                    
                    data = await response.json()
                    _LOGGER.debug("Received data: %s", data)
                    return data
                    
        except aiohttp.ClientError as err:
            raise CannotConnect(f"Error connecting to API: {err}") from err
        except asyncio.TimeoutError as err:
            raise CannotConnect(f"Timeout connecting to API: {err}") from err

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def get_stove_data(self) -> StoveData:
        """Get current stove data."""
        try:
            data = await self._request("GET", ENDPOINT_GET_STOVE_DATA)
            return StoveData.from_dict(data)
        except Exception as err:
            _LOGGER.error("Error getting stove data: %s", err)
            raise

    async def set_burn_level(self, level: int) -> bool:
        """Set burn level (0-5)."""
        if not 0 <= level <= 5:
            raise ValueError("Burn level must be between 0 and 5")
            
        try:
            data = await self._request(
                "POST", 
                ENDPOINT_SET_BURN_LEVEL, 
                data={"level": level}
            )
            return data.get("response") == "OK"
        except Exception as err:
            _LOGGER.error("Error setting burn level: %s", err)
            raise

    async def start_combustion(self) -> bool:
        """Start combustion process."""
        try:
            data = await self._request("GET", ENDPOINT_START)
            return data.get("response") == "OK"
        except Exception as err:
            _LOGGER.error("Error starting combustion: %s", err)
            raise

    async def set_night_time(
        self, 
        start_time: datetime.time, 
        end_time: datetime.time
    ) -> bool:
        """Set night mode time period."""
        try:
            data = await self._request(
                "POST",
                ENDPOINT_SET_NIGHT_TIME,
                data={
                    "begin_hour": start_time.hour,
                    "begin_minute": start_time.minute,
                    "end_hour": end_time.hour,
                    "end_minute": end_time.minute,
                }
            )
            return data.get("response") == "OK"
        except Exception as err:
            _LOGGER.error("Error setting night time: %s", err)
            raise

    async def test_connection(self) -> bool:
        """Test connectivity to HWAM stove."""
        try:
            await self.get_stove_data()
            return True
        except Exception:
            return False
