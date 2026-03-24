"""FEWS NET IPC food security cache-warming pipeline (query-on-demand)."""

import json
import logging
import os
from typing import Any, Dict, List

import httpx
import redis

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

FEWS_NET_URL = "https://fdw.fews.net/api/ipcpacket/"
CACHE_TTL = int(os.getenv("CACHE_TTL_FOOD_SECURITY", "604800"))


class FEWSNetPipeline(BaseETLPipeline):
    """Warms the Redis cache with FEWS NET IPC food security phase data.

    No data is stored in the database — results are cached in Redis.
    Query metadata is logged to Supabase ``ingestion_logs``.
    """

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "FEWS NET")
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0")
        )
        self.target_countries = os.getenv("TARGET_COUNTRIES", "KEN,ETH,NGA").split(",")

    def extract(self) -> Any:
        results = []
        for country in self.target_countries:
            cache_key = f"fews_net:ipc:{country}:None:None"
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.debug("Cache hit for FEWS NET country=%s", country)
                results.append({"country": country, "cached": True})
                continue
            logger.info("Fetching FEWS NET IPC data for country=%s", country)
            try:
                with httpx.Client(timeout=120) as client:
                    resp = client.get(
                        FEWS_NET_URL,
                        params={"country_code": country, "format": "json"},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    self.redis_client.setex(cache_key, CACHE_TTL, json.dumps(data))
                    results.append({"country": country, "cached": False})
            except Exception as exc:
                logger.warning("FEWS NET unavailable for country=%s: %s", country, exc)
                results.append({"country": country, "cached": False, "error": str(exc)})
        return results

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        return raw_data

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Log cache-warming metadata to Supabase ingestion_logs."""
        failed = sum(1 for r in data if r.get("error"))
        return {"rows_processed": len(data) - failed, "rows_failed": failed}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = FEWSNetPipeline(db_url)
    pipeline.run()
