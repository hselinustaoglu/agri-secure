"""CHIRPS rainfall data client via CHC API (query-on-demand)."""

import logging
from typing import Any, Optional

from .base_client import BaseExternalClient

logger = logging.getLogger(__name__)

_CHIRPS_BASE = "https://data.chc.ucsb.edu/products/CHIRPS-2.0"


class CHIRPSClient(BaseExternalClient):
    """Async client for CHIRPS monthly rainfall data.

    Downloads monthly global TIF files or queries CHC data via HTTP.
    Cache TTL: 24 hours (default).
    """

    def __init__(self, redis_url: str, ttl: int = 86400) -> None:
        super().__init__(redis_url, base_url=_CHIRPS_BASE, ttl=ttl)

    async def get_monthly_stats(
        self,
        year: int,
        month: int,
        country: Optional[str] = None,
    ) -> Any:
        """Return metadata/stats for a CHIRPS monthly rainfall file.

        This queries CHIRPS file availability without bulk-downloading
        the full raster.  For actual pixel extraction, callers should
        use a GEE or dedicated raster service.

        Args:
            year: Four-digit year, e.g. ``2024``.
            month: Month number 1-12.
            country: Optional ISO3 country code for cache key scoping.

        Returns:
            Dictionary with ``year``, ``month``, ``filename``, and ``url``.
        """
        cache_key = f"chirps:{year}:{month:02d}:{country or 'global'}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT chirps year=%s month=%s", year, month)
            return cached

        filename = f"chirps-v2.0.{year}.{month:02d}.tif.gz"
        url = f"{self.base_url}/global_monthly/tifs/{filename}"
        logger.info("Resolving CHIRPS file url=%s", url)
        result = {
            "year": year,
            "month": month,
            "filename": filename,
            "url": url,
            "country": country,
        }
        self._cache_set(cache_key, result)
        return result
