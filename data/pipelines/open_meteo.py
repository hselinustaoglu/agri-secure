"""Open-Meteo weather forecast pipeline with Redis caching."""

import json
import logging
import os
import uuid
from typing import Any, Dict, List

import httpx
import redis
from sqlalchemy import text

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL = 6 * 3600


class OpenMeteoPipeline(BaseETLPipeline):
    """Downloads weather forecasts from Open-Meteo API with Redis caching."""

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
        results = []
        for lat, lon in self.locations:
            cache_key = f"open_meteo:{lat}:{lon}"
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.debug("Cache hit for location %s,%s", lat, lon)
                results.append(json.loads(cached))
                continue
            logger.info("Fetching Open-Meteo forecast for %s,%s", lat, lon)
            with httpx.Client(timeout=30) as client:
                resp = client.get(
                    OPEN_METEO_URL,
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
                        "forecast_days": 7,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                data["_lat"] = lat
                data["_lon"] = lon
                self.redis_client.setex(cache_key, CACHE_TTL, json.dumps(data))
                results.append(data)
        return results

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        for location_data in raw_data:
            lat = location_data.get("_lat")
            lon = location_data.get("_lon")
            hourly = location_data.get("hourly", {})
            times = hourly.get("time", [])
            temperatures = hourly.get("temperature_2m", [])
            humidities = hourly.get("relative_humidity_2m", [])
            wind_speeds = hourly.get("wind_speed_10m", [])
            precipitations = hourly.get("precipitation", [])
            for i, forecast_time in enumerate(times):
                records.append(
                    {
                        "lat": lat,
                        "lon": lon,
                        "forecast_date": forecast_time,
                        "temperature": (
                            temperatures[i] if i < len(temperatures) else None
                        ),
                        "humidity": humidities[i] if i < len(humidities) else None,
                        "wind_speed": wind_speeds[i] if i < len(wind_speeds) else None,
                        "precipitation": (
                            precipitations[i] if i < len(precipitations) else None
                        ),
                    }
                )
        logger.info("Transformed %d Open-Meteo weather records", len(records))
        return records

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        if not data:
            logger.warning("No Open-Meteo records to load")
            return {"rows_processed": 0, "rows_failed": 0}
        rows_processed = 0
        rows_failed = 0
        with self.SessionLocal() as session:
            for record in data:
                try:
                    location_wkt = (
                        f"SRID=4326;POINT({record['lon']} {record['lat']})"
                        if record["lat"] is not None
                        else None
                    )
                    session.execute(
                        text(
                            "INSERT INTO weather_data "
                            "(id, location, temperature, humidity, wind_speed, precipitation, forecast_date, source) "
                            "VALUES (:id, ST_GeomFromEWKT(:location), :temperature, :humidity, "
                            ":wind_speed, :precipitation, :forecast_date, 'open_meteo')"
                        ),
                        {
                            "id": str(uuid.uuid4()),
                            "location": location_wkt,
                            "temperature": record["temperature"],
                            "humidity": record["humidity"],
                            "wind_speed": record["wind_speed"],
                            "precipitation": record["precipitation"],
                            "forecast_date": record["forecast_date"],
                        },
                    )
                    rows_processed += 1
                except Exception as exc:
                    logger.error("Failed to insert Open-Meteo record: %s", exc)
                    rows_failed += 1
            session.commit()
        return {"rows_processed": rows_processed, "rows_failed": rows_failed}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = OpenMeteoPipeline(db_url)
    pipeline.run()
