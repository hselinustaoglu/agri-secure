"""WFP VAM Data Bridges food prices client (query-on-demand)."""

import logging
from typing import Any, Optional

from .base_client import BaseExternalClient

logger = logging.getLogger(__name__)


class WFPClient(BaseExternalClient):
    """Async client for WFP VAM Data Bridges API.

    Endpoint: GET /vam-data-bridges/4.0.0/MarketPrices/...
    Cache TTL: 24 hours (default).
    """

    def __init__(self, redis_url: str, base_url: str, ttl: int = 86400) -> None:
        super().__init__(redis_url, base_url=base_url, ttl=ttl)

    async def get_prices(
        self,
        country_code: Optional[str] = None,
        commodity: Optional[str] = None,
        page: int = 1,
    ) -> Any:
        """Query WFP market prices via VAM Data Bridges.

        Args:
            country_code: ISO3 country code, e.g. ``KEN``.
            commodity: Commodity name or code.
            page: Pagination page number.

        Returns:
            Parsed JSON response from WFP API.
        """
        cache_key = f"wfp:prices:{country_code}:{commodity}:{page}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT wfp prices country=%s", country_code)
            return cached

        logger.info(
            "Fetching WFP prices country=%s commodity=%s", country_code, commodity
        )
        params: dict = {"page": page, "format": "json"}
        if country_code:
            params["CountryCode"] = country_code
        if commodity:
            params["Commodity"] = commodity

        data = await self._get(
            f"{self.base_url}/MarketPrices/PriceMonthly",
            params=params,
        )
        self._cache_set(cache_key, data)
        return data
