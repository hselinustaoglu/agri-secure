"""FEWS NET IPC food insecurity client (query-on-demand)."""

import logging
from typing import Any, Optional

from .base_client import BaseExternalClient

logger = logging.getLogger(__name__)


class FEWSNetClient(BaseExternalClient):
    """Async client for FEWS NET food security data API.

    Endpoint: GET /api/ipcpacket/ or FEWS NET GeoJSON endpoints
    Cache TTL: 7 days (default).
    """

    def __init__(self, redis_url: str, base_url: str, ttl: int = 604800) -> None:
        super().__init__(redis_url, base_url=base_url, ttl=ttl)

    async def get_ipc_data(
        self,
        country_code: Optional[str] = None,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
    ) -> Any:
        """Query FEWS NET IPC phase classifications.

        Args:
            country_code: ISO2/ISO3 country code, e.g. ``KE`` or ``KEN``.
            period_start: Start date in YYYY-MM-DD format.
            period_end: End date in YYYY-MM-DD format.

        Returns:
            Parsed JSON IPC data from FEWS NET.
        """
        cache_key = f"fews_net:ipc:{country_code}:{period_start}:{period_end}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT fews_net country=%s", country_code)
            return cached

        logger.info("Fetching FEWS NET IPC country=%s", country_code)
        params: dict = {"format": "json"}
        if country_code:
            params["country_code"] = country_code
        if period_start:
            params["period_start"] = period_start
        if period_end:
            params["period_end"] = period_end

        data = await self._get(
            f"{self.base_url}/ipcpacket/",
            params=params,
        )
        self._cache_set(cache_key, data)
        return data
