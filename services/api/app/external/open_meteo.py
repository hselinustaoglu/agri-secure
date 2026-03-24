"""Open-Meteo weather forecast client (query-on-demand)."""

import logging
from typing import Any, Optional

from .base_client import BaseExternalClient

logger = logging.getLogger(__name__)


class OpenMeteoClient(BaseExternalClient):
    """Async client for Open-Meteo free weather forecast API.

    Endpoint: GET /v1/forecast?latitude=X&longitude=Y&daily=...
    Cache TTL: 1 hour (default).
    """

    def __init__(self, redis_url: str, base_url: str, ttl: int = 3600) -> None:
        super().__init__(redis_url, base_url=base_url, ttl=ttl)

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        daily: Optional[str] = None,
    ) -> Any:
        """Return 7-day daily forecast for the given coordinates.

        Args:
            latitude: WGS-84 latitude.
            longitude: WGS-84 longitude.
            daily: Comma-separated list of daily variables.
                   Defaults to temperature_2m_max,precipitation_sum,soil_moisture_0_to_7cm.

        Returns:
            Parsed JSON response from Open-Meteo.
        """
        if daily is None:
            daily = "temperature_2m_max,precipitation_sum,soil_moisture_0_to_7cm"

        cache_key = f"open_meteo:{latitude}:{longitude}:{daily}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT open_meteo lat=%s lon=%s", latitude, longitude)
            return cached

        logger.info("Fetching Open-Meteo forecast lat=%s lon=%s", latitude, longitude)
        data = await self._get(
            f"{self.base_url}/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": daily,
                "forecast_days": 7,
            },
        )
        self._cache_set(cache_key, data)
        return data
