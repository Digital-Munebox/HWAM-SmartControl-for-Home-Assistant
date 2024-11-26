"""HWAM Smart Control API Client."""
from datetime import datetime
import logging
from typing import Optional
import ssl

import aiohttp
import async_timeout
from tenacity import retry, stop_after_attempt, wait_exponential

from .const import (
    ENDPOINT_GET_STOVE_DATA,
    ENDPOINT_SET_BURN_LEVEL,
    ENDPOINT_START,
    ENDPOINT_SET_NIGHT_TIME,
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
)
from .models import StoveData

_LOGGER = logging.getLogger(__name__)

class HWAMApiError(Exception):
    """Exception de base pour les erreurs API HWAM."""
    pass

class CannotConnect(HWAMApiError):
    """Erreur de connexion."""
    pass

class InvalidResponse(HWAMApiError):
    """Réponse API invalide."""
    pass

class InvalidAuth(HWAMApiError):
    """Erreur d'authentification."""
    pass

class HWAMApi:
    """Client API HWAM Smart Control."""

    def __init__(
        self, 
        host: str, 
        session: Optional[aiohttp.ClientSession] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = False,
        request_timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the API client."""
        self._host = host
        self._session = session
        self._request_timeout = request_timeout
        self._username = username
        self._password = password
        self._close_session = False
        self._ssl_context = ssl.create_default_context() if use_ssl else False
        self._base_url = f"{'https' if use_ssl else 'http'}://{host}"
        self._cached_data: Optional[StoveData] = None
        self._last_update: Optional[datetime] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get aiohttp session."""
        if self._session is None:
            auth = None
            if self._username and self._password:
                auth = aiohttp.BasicAuth(self._username, self._password)
                
            self._session = aiohttp.ClientSession(
                auth=auth,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "HWAM-HA-Integration/1.0",
                }
            )
            self._close_session = True
        return self._session

    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[dict] = None, 
        data: Optional[dict] = None
    ) -> dict:
        """Make request to API with retry logic."""
        session = await self._get_session()
        url = f"{self._base_url}{endpoint}"

        try:
            async with async_timeout.timeout(self._request_timeout):
                _LOGGER.debug("Making %s request to %s", method, url)
                async with session.request(
                    method, 
                    url, 
                    params=params, 
                    json=data,
                    ssl=self._ssl_context,
                ) as response:
                    if response.status == 401:
                        raise InvalidAuth("Authentication invalide")
                    
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
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_stove_data(self) -> StoveData:
        """Get current stove data with retry logic."""
        try:
            data = await self._request("GET", ENDPOINT_GET_STOVE_DATA)
            stove_data = StoveData.from_dict(data)
            
            # Mise en cache des données
            self._cached_data = stove_data
            self._last_update = datetime.now()
            
            return stove_data
            
        except Exception as err:
            _LOGGER.error("Error getting stove data: %s", err)
            # Utiliser les données en cache si disponibles
            if self._cached_data is not None:
                _LOGGER.warning("Using cached data from %s", self._last_update)
                return self._cached_data
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
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    @property
    def cache_age(self) -> Optional[timedelta]:
        """Get age of cached data."""
        if self._last_update is None:
            return None
        return datetime.now() - self._last_update

    def clear_cache(self) -> None:
        """Clear cached data."""
        self._cached_data = None
        self._last_update = None
