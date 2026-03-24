"""HeiGIT risk and accessibility data client via HDX CKAN API (query-on-demand)."""

import logging
from typing import Any, Optional

from .base_client import BaseExternalClient

logger = logging.getLogger(__name__)


class HeiGITClient(BaseExternalClient):
    """Async client for HeiGIT datasets via HDX CKAN API.

    Endpoint: GET /api/3/action/package_search?q=heigit&...
    Cache TTL: 7 days (default).
    """

    def __init__(self, redis_url: str, base_url: str, ttl: int = 604800) -> None:
        super().__init__(redis_url, base_url=base_url, ttl=ttl)

    async def search_datasets(
        self,
        query: str = "heigit",
        rows: int = 10,
        country: Optional[str] = None,
    ) -> Any:
        """Search HDX CKAN for HeiGIT datasets.

        Args:
            query: Full-text search query, e.g. ``heigit risk`` or
                   ``heigit accessibility``.
            rows: Maximum number of results to return.
            country: Optional ISO3 country code to scope search.

        Returns:
            Parsed JSON CKAN package_search response.
        """
        cache_key = f"heigit:datasets:{query}:{rows}:{country or 'all'}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT heigit query=%s", query)
            return cached

        logger.info("Searching HDX for HeiGIT datasets query=%s", query)
        params: dict = {"q": query, "rows": rows}
        if country:
            params["fq"] = f"groups:{country.lower()}"

        data = await self._get(
            f"{self.base_url}/action/package_search",
            params=params,
        )
        self._cache_set(cache_key, data)
        return data

    async def get_risk_datasets(self, country: Optional[str] = None) -> Any:
        """Return HeiGIT risk indicator datasets from HDX."""
        return await self.search_datasets(query="heigit risk", country=country)

    async def get_accessibility_datasets(self, country: Optional[str] = None) -> Any:
        """Return HeiGIT accessibility datasets from HDX."""
        return await self.search_datasets(query="heigit accessibility", country=country)
