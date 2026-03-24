"""FEWS NET IPC food security pipeline."""

import logging
import os
import uuid
from typing import Any, Dict, List

import httpx
from sqlalchemy import text

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

FEWS_NET_URL = "https://fdw.fews.net/api/ipcpacket/"


class FEWSNetPipeline(BaseETLPipeline):
    """Downloads IPC food security phase data from FEWS NET."""

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "FEWS NET")
        self.target_countries = os.getenv("TARGET_COUNTRIES", "KEN,ETH,NGA").split(",")

    def extract(self) -> Any:
        logger.info("Fetching FEWS NET IPC data from %s", FEWS_NET_URL)
        params = {
            "country_code": ",".join(self.target_countries),
            "format": "json",
        }
        with httpx.Client(timeout=120) as client:
            resp = client.get(FEWS_NET_URL, params=params)
            resp.raise_for_status()
            return resp.json()

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        items = raw_data if isinstance(raw_data, list) else raw_data.get("results", [])
        for item in items:
            records.append(
                {
                    "country_code": item.get("country", ""),
                    "period_start": item.get("period_start"),
                    "period_end": item.get("period_end"),
                    "ipc_phase": item.get("ipc_phase"),
                    "population": item.get("population_affected"),
                    "region_name": item.get("admin1_name", ""),
                }
            )
        logger.info("Transformed %d FEWS NET records", len(records))
        return records

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        if not data:
            logger.warning("No FEWS NET records to load")
            return {"rows_processed": 0, "rows_failed": 0}
        rows_processed = 0
        rows_failed = 0
        with self.SessionLocal() as session:
            for record in data:
                try:
                    region_row = session.execute(
                        text(
                            "SELECT id FROM regions WHERE country_code = :cc "
                            "AND name = :name LIMIT 1"
                        ),
                        {
                            "cc": record["country_code"],
                            "name": record["region_name"],
                        },
                    ).fetchone()
                    region_id = str(region_row[0]) if region_row else None
                    session.execute(
                        text(
                            "INSERT INTO food_security_indicators "
                            "(id, region_id, indicator_type, value, period_start, period_end, source) "
                            "VALUES (:id, :region_id, 'ipc_phase', :value, :period_start, :period_end, 'fews_net') "
                            "ON CONFLICT DO NOTHING"
                        ),
                        {
                            "id": str(uuid.uuid4()),
                            "region_id": region_id,
                            "value": record["ipc_phase"],
                            "period_start": record["period_start"],
                            "period_end": record["period_end"],
                        },
                    )
                    rows_processed += 1
                except Exception as exc:
                    logger.error("Failed to insert FEWS NET record: %s", exc)
                    rows_failed += 1
            session.commit()
        return {"rows_processed": rows_processed, "rows_failed": rows_failed}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = FEWSNetPipeline(db_url)
    pipeline.run()
