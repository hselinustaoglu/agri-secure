"""FAOSTAT food production data cache-warming pipeline (query-on-demand)."""

import json
import logging
import os
from typing import Any, Dict, List

import httpx
import redis

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

FAOSTAT_BASE_URL = os.getenv(
    "FAOSTAT_BASE_URL", "https://fenixservices.fao.org/faostat/api/v1"
)
CACHE_TTL = int(os.getenv("CACHE_TTL_PRICES", "86400"))


class FAOSTATPipeline(BaseETLPipeline):
    """Warms the Redis cache with FAOSTAT crop production and food security data.

    No data is stored in the database — results are cached in Redis.
    Query metadata is logged to Supabase ``ingestion_logs``.
    """

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "FAOSTAT")
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0")
        )
        self.target_countries = os.getenv("TARGET_COUNTRIES", "KEN,ETH,NGA").split(",")

    def extract(self) -> Any:
        area = ",".join(self.target_countries)
        cache_key = f"faostat:QCL:{area}:None:2022,2023"
        cached = self.redis_client.get(cache_key)
        if cached:
            logger.debug("Cache hit for FAOSTAT")
            return {"cached": True, "countries": self.target_countries}

        logger.info("Fetching FAOSTAT data for countries=%s", area)
        params = {
            "area": area,
            "element": "5510",
            "year": "2022,2023",
            "output_type": "json",
        }
        with httpx.Client(timeout=120) as client:
            resp = client.get(f"{FAOSTAT_BASE_URL}/en/data/QCL", params=params)
            resp.raise_for_status()
            data = resp.json()
            self.redis_client.setex(cache_key, CACHE_TTL, json.dumps(data))
            return {
                "cached": False,
                "countries": self.target_countries,
                "records": len(data.get("data", [])),
            }

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        return [raw_data] if isinstance(raw_data, dict) else raw_data

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Log cache-warming metadata to Supabase ingestion_logs."""
        return {"rows_processed": len(data), "rows_failed": 0}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = FAOSTATPipeline(db_url)
    pipeline.run()
