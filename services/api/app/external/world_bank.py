"""World Bank Real-Time Food Prices (RTFP) client (query-on-demand)."""

import logging
from typing import Any

from .base_client import BaseExternalClient

logger = logging.getLogger(__name__)

_CATALOG_ID = "4483"


class WorldBankClient(BaseExternalClient):
    """Async client for World Bank RTFP catalog (microdata catalog 4483).

    Endpoint: GET https://microdata.worldbank.org/index.php/api/catalog/{id}
    Cache TTL: 24 hours (default).
    """

    def __init__(self, redis_url: str, base_url: str, ttl: int = 86400) -> None:
        super().__init__(redis_url, base_url=base_url, ttl=ttl)

    async def get_catalog(self, catalog_id: str = _CATALOG_ID) -> Any:
        """Return catalog metadata for the RTFP dataset.

        Args:
            catalog_id: World Bank microdata catalog ID (default ``4483``).

        Returns:
            Parsed JSON catalog metadata.
        """
        cache_key = f"world_bank:catalog:{catalog_id}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT world_bank catalog=%s", catalog_id)
            return cached

        logger.info("Fetching World Bank catalog id=%s", catalog_id)
        url = f"https://microdata.worldbank.org/index.php/api/catalog/{catalog_id}"
        data = await self._get(url, params={"format": "json"})
        self._cache_set(cache_key, data)
        return data

    async def get_indicators(self, country: str, indicator: str = "FP.CPI.TOTL") -> Any:
        """Query World Bank indicators API for a country.

        Args:
            country: ISO2 country code, e.g. ``KE``.
            indicator: World Bank indicator code.

        Returns:
            Parsed JSON response.
        """
        cache_key = f"world_bank:indicator:{country}:{indicator}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            logger.debug(
                "Cache HIT world_bank indicator=%s country=%s", indicator, country
            )
            return cached

        logger.info("Fetching World Bank indicator=%s country=%s", indicator, country)
        data = await self._get(
            f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}",
            params={"format": "json", "per_page": 100},
        )
        self._cache_set(cache_key, data)
        return data
