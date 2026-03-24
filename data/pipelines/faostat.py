"""FAOSTAT food production data pipeline."""

import logging
import os
import uuid
from typing import Any, Dict, List

import httpx
from sqlalchemy import text

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

FAOSTAT_URL = "https://fenixservices.fao.org/faostat/api/v1/en/data/QCL"


class FAOSTATPipeline(BaseETLPipeline):
    """Downloads crop production data from FAOSTAT."""

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "FAOSTAT")
        self.target_countries = os.getenv("TARGET_COUNTRIES", "KEN,ETH,NGA").split(",")

    def extract(self) -> Any:
        logger.info("Fetching FAOSTAT data from %s", FAOSTAT_URL)
        params = {
            "area": ",".join(self.target_countries),
            "element": "5510",
            "year": "2022,2023",
            "output_type": "json",
        }
        with httpx.Client(timeout=120) as client:
            resp = client.get(FAOSTAT_URL, params=params)
            resp.raise_for_status()
            return resp.json()

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        items = raw_data.get("data", []) if isinstance(raw_data, dict) else []
        for item in items:
            records.append(
                {
                    "country_code": item.get("Area Code (ISO3)", ""),
                    "commodity": item.get("Item", ""),
                    "year": item.get("Year"),
                    "value": item.get("Value"),
                    "unit": item.get("Unit", ""),
                }
            )
        logger.info("Transformed %d FAOSTAT records", len(records))
        return records

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        if not data:
            logger.warning("No FAOSTAT records to load")
            return {"rows_processed": 0, "rows_failed": 0}
        rows_processed = 0
        rows_failed = 0
        with self.SessionLocal() as session:
            for record in data:
                try:
                    region_row = session.execute(
                        text(
                            "SELECT id FROM regions WHERE country_code = :cc "
                            "AND admin_level = 0 LIMIT 1"
                        ),
                        {"cc": record["country_code"]},
                    ).fetchone()
                    if not region_row:
                        rows_failed += 1
                        continue
                    session.execute(
                        text(
                            "INSERT INTO risk_assessments "
                            "(id, admin_area_id, indicator_type, value, assessment_date, source) "
                            "VALUES (:id, :area_id, :indicator_type, :value, CURRENT_DATE, 'fao') "
                            "ON CONFLICT DO NOTHING"
                        ),
                        {
                            "id": str(uuid.uuid4()),
                            "area_id": str(region_row[0]),
                            "indicator_type": f"faostat_production_{record['commodity']}",
                            "value": record["value"],
                        },
                    )
                    rows_processed += 1
                except Exception as exc:
                    logger.error("Failed to insert FAOSTAT record: %s", exc)
                    rows_failed += 1
            session.commit()
        return {"rows_processed": rows_processed, "rows_failed": rows_failed}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = FAOSTATPipeline(db_url)
    pipeline.run()
