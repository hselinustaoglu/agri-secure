"""HeiGIT risk data cache-warming pipeline (query-on-demand)."""

import json
import logging
import os
from typing import Any, Dict, List

import httpx
import redis

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

HDX_SEARCH_URL = "https://data.humdata.org/api/3/action/package_search"
CACHE_TTL = int(os.getenv("CACHE_TTL_FOOD_SECURITY", "604800"))


class HeiGITRiskPipeline(BaseETLPipeline):
    """Warms the Redis cache with HeiGIT risk dataset metadata from HDX.

    No data is stored in the database — results are cached in Redis.
    Query metadata is logged to Supabase ``ingestion_logs``.
    """

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "HeiGIT Risk")
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0")
        )
        self.target_countries = os.getenv("TARGET_COUNTRIES", "KEN,ETH,NGA").split(",")

    def extract(self) -> Any:
        cache_key = "heigit:datasets:heigit risk:10:all"
        cached = self.redis_client.get(cache_key)
        if cached:
            logger.debug("Cache hit for HeiGIT risk datasets")
            return json.loads(cached)

        logger.info("Searching HDX for HeiGIT risk datasets")
        with httpx.Client(timeout=60) as client:
            resp = client.get(
                HDX_SEARCH_URL,
                params={"q": "heigit risk", "rows": 10},
            )
            resp.raise_for_status()
            data = resp.json()
            self.redis_client.setex(cache_key, CACHE_TTL, json.dumps(data))
            return data

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        result = raw_data.get("result", {}) if isinstance(raw_data, dict) else {}
        datasets = result.get("results", [])
        return [
            {
                "dataset_name": d.get("name", ""),
                "resource_count": len(d.get("resources", [])),
            }
            for d in datasets
        ]

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Log cache-warming metadata to Supabase ingestion_logs."""
        return {"rows_processed": len(data), "rows_failed": 0}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = HeiGITRiskPipeline(db_url)
    pipeline.run()
