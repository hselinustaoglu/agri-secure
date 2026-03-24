"""World Bank Real-Time Food Prices (RTFP) cache-warming pipeline (query-on-demand)."""

import json
import logging
import os
from typing import Any, Dict, List

import httpx
import redis

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

CATALOG_URL = "https://microdata.worldbank.org/index.php/api/catalog/4483"
CACHE_TTL = int(os.getenv("CACHE_TTL_PRICES", "86400"))


class WorldBankRTFPPipeline(BaseETLPipeline):
    """Warms the Redis cache with World Bank RTFP catalog metadata.

    No data is stored in the database — results are cached in Redis.
    Query metadata is logged to Supabase ``ingestion_logs``.
    """

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "World Bank RTFP")
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0")
        )
        self.target_countries = os.getenv("TARGET_COUNTRIES", "KEN,ETH,NGA").split(",")

    def extract(self) -> Any:
        cache_key = "world_bank:catalog:4483"
        cached = self.redis_client.get(cache_key)
        if cached:
            logger.debug("Cache hit for World Bank RTFP catalog")
            return json.loads(cached)

        logger.info("Fetching World Bank RTFP catalog from %s", CATALOG_URL)
        with httpx.Client(timeout=60) as client:
            resp = client.get(CATALOG_URL, params={"format": "json"})
            resp.raise_for_status()
            data = resp.json()
            self.redis_client.setex(cache_key, CACHE_TTL, json.dumps(data))
            return data

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Return summary metadata for logging."""
        study = raw_data if isinstance(raw_data, dict) else {}
        return [{"catalog_id": study.get("id", "4483"), "cached": True}]

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Log cache-warming metadata to Supabase ingestion_logs."""
        return {"rows_processed": len(data), "rows_failed": 0}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = WorldBankRTFPPipeline(db_url)
    pipeline.run()
