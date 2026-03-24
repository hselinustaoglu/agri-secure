"""FAOSTAT crop production and food security client (query-on-demand)."""

import logging
from typing import Any, Optional

from .base_client import BaseExternalClient

logger = logging.getLogger(__name__)


class FAOSTATClient(BaseExternalClient):
    """Async client for FAOSTAT open data API.

    Endpoint: GET /faostat/api/v1/en/data/{domain}?area={code}&item={code}&year={year}
    Cache TTL: 24 hours (default).
    """

    def __init__(self, redis_url: str, base_url: str, ttl: int = 86400) -> None:
        super().__init__(redis_url, base_url=base_url, ttl=ttl)

    async def get_data(
        self,
        domain: str = "QCL",
        area: Optional[str] = None,
        item: Optional[str] = None,
        year: Optional[str] = None,
    ) -> Any:
        """Query FAOSTAT for crop production or food balance data.

        Args:
            domain: FAOSTAT domain code, e.g. ``QCL`` (crop production),
                    ``FBS`` (food balance sheets), ``FS`` (food security indicators).
            area: ISO3 country code(s), comma-separated, e.g. ``KEN,ETH``.
            item: Item code(s), comma-separated.
            year: Year(s), e.g. ``2022,2023``.

        Returns:
            Parsed JSON response from FAOSTAT.
        """
        cache_key = f"faostat:{domain}:{area}:{item}:{year}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT faostat domain=%s area=%s", domain, area)
            return cached

        logger.info("Fetching FAOSTAT domain=%s area=%s year=%s", domain, area, year)
        params: dict = {"output_type": "json"}
        if area:
            params["area"] = area
        if item:
            params["item"] = item
        if year:
            params["year"] = year

        data = await self._get(
            f"{self.base_url}/en/data/{domain}",
            params=params,
        )
        self._cache_set(cache_key, data)
        return data
