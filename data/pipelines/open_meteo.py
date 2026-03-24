"""Open-Meteo weather cache-warming pipeline (query-on-demand)."""

import json
import logging
import os
from typing import Any, Dict, List

import httpx
import redis

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL = int(os.getenv("CACHE_TTL_WEATHER", "3600"))


class OpenMeteoPipeline(BaseETLPipeline):
    """Warms the Redis cache with weather forecasts from Open-Meteo.

    No data is stored in the database — results are cached in Redis with a
    configurable TTL.  Query metadata (what was queried, status) is logged
    to the Supabase ``ingestion_logs`` table via the base class.
    """

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "Open-Meteo")
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0")
        )
        raw_locations = os.getenv(
            "WEATHER_LOCATIONS",
            "-1.286389,36.817223;9.145000,40.489673;9.082000,8.675277",
        )
        self.locations = [
            tuple(map(float, loc.split(","))) for loc in raw_locations.split(";") if loc
        ]

    def extract(self) -> Any:
        """Query Open-Meteo for each configured location and cache the result."""
        results = []
        for lat, lon in self.locations:
            cache_key = f"open_meteo:{lat}:{lon}"
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.debug("Cache hit for location %s,%s", lat, lon)
                results.append({"lat": lat, "lon": lon, "cached": True})
                continue
            logger.info("Fetching Open-Meteo forecast for %s,%s", lat, lon)
            with httpx.Client(timeout=30) as client:
                resp = client.get(
                    OPEN_METEO_URL,
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "daily": "temperature_2m_max,precipitation_sum,soil_moisture_0_to_7cm",
                        "forecast_days": 7,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                data["_lat"] = lat
                data["_lon"] = lon
                self.redis_client.setex(cache_key, CACHE_TTL, json.dumps(data))
                results.append({"lat": lat, "lon": lon, "cached": False})
        return results

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Return a summary of locations queried for metadata logging."""
        return raw_data

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Log cache-warming metadata to Supabase ingestion_logs."""
        return {"rows_processed": len(data), "rows_failed": 0}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = OpenMeteoPipeline(db_url)
    pipeline.run()
