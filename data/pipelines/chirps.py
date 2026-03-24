"""CHIRPS rainfall cache-warming pipeline (query-on-demand)."""

import json
import logging
import os
from typing import Any, Dict, List

import redis

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

CHIRPS_BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/"
CACHE_TTL = int(os.getenv("CACHE_TTL_PRICES", "86400"))


class CHIRPSPipeline(BaseETLPipeline):
    """Warms the Redis cache with CHIRPS monthly rainfall file metadata.

    Instead of downloading large TIF rasters, this pipeline caches the
    file URL and metadata in Redis with a configurable TTL.
    Query metadata is logged to Supabase ``ingestion_logs``.
    """

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "CHIRPS")
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0")
        )
        self.target_countries = os.getenv("TARGET_COUNTRIES", "KEN,ETH,NGA").split(",")

    def _latest_year_month(self) -> tuple:
        import datetime

        now = datetime.datetime.utcnow()
        month = now.month - 1 if now.month > 1 else 12
        year = now.year if now.month > 1 else now.year - 1
        return year, month

    def extract(self) -> Any:
        year, month = self._latest_year_month()
        results = []
        for country in self.target_countries:
            cache_key = f"chirps:{year}:{month:02d}:{country}"
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.debug(
                    "Cache hit for CHIRPS year=%s month=%s country=%s",
                    year,
                    month,
                    country,
                )
                results.append(
                    {"country": country, "year": year, "month": month, "cached": True}
                )
                continue
            filename = f"chirps-v2.0.{year}.{month:02d}.tif.gz"
            metadata = {
                "year": year,
                "month": month,
                "filename": filename,
                "url": f"{CHIRPS_BASE_URL}{filename}",
                "country": country,
            }
            self.redis_client.setex(cache_key, CACHE_TTL, json.dumps(metadata))
            logger.info(
                "Cached CHIRPS metadata for year=%s month=%s country=%s",
                year,
                month,
                country,
            )
            results.append(
                {"country": country, "year": year, "month": month, "cached": False}
            )
        return results

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        return raw_data

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Log cache-warming metadata to Supabase ingestion_logs."""
        return {"rows_processed": len(data), "rows_failed": 0}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = CHIRPSPipeline(db_url)
    pipeline.run()
