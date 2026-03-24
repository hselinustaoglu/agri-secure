"""HeiGIT risk data pipeline from HDX."""

import logging
import os
import uuid
from typing import Any, Dict, List

import httpx
from sqlalchemy import text

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

HDX_SEARCH_URL = "https://data.humdata.org/api/3/action/package_search"


class HeiGITRiskPipeline(BaseETLPipeline):
    """Downloads HeiGIT risk indicators from HDX."""

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "HeiGIT Risk")
        self.target_countries = os.getenv("TARGET_COUNTRIES", "KEN,ETH,NGA").split(",")

    def extract(self) -> Any:
        logger.info("Searching HDX for HeiGIT risk datasets")
        with httpx.Client(timeout=60) as client:
            resp = client.get(
                HDX_SEARCH_URL,
                params={"q": "heigit risk", "rows": 10},
            )
            resp.raise_for_status()
            return resp.json()

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        result = raw_data.get("result", {}) if isinstance(raw_data, dict) else {}
        datasets = result.get("results", [])
        for dataset in datasets:
            for resource in dataset.get("resources", []):
                records.append(
                    {
                        "dataset_name": dataset.get("name", ""),
                        "resource_url": resource.get("url", ""),
                        "format": resource.get("format", ""),
                        "description": resource.get("description", ""),
                    }
                )
        logger.info("Found %d HeiGIT risk resources", len(records))
        return records

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        if not data:
            logger.warning("No HeiGIT risk records to load")
            return {"rows_processed": 0, "rows_failed": 0}
        rows_processed = 0
        rows_failed = 0
        with self.SessionLocal() as session:
            for record in data:
                try:
                    for country_code in self.target_countries:
                        region_row = session.execute(
                            text(
                                "SELECT id FROM regions WHERE country_code = :cc "
                                "AND admin_level = 0 LIMIT 1"
                            ),
                            {"cc": country_code},
                        ).fetchone()
                        if not region_row:
                            continue
                        session.execute(
                            text(
                                "INSERT INTO vulnerability_indicators "
                                "(id, admin_area_id) "
                                "VALUES (:id, :area_id) "
                                "ON CONFLICT DO NOTHING"
                            ),
                            {
                                "id": str(uuid.uuid4()),
                                "area_id": str(region_row[0]),
                            },
                        )
                        rows_processed += 1
                except Exception as exc:
                    logger.error("Failed to insert HeiGIT risk record: %s", exc)
                    rows_failed += 1
            session.commit()
        return {"rows_processed": rows_processed, "rows_failed": rows_failed}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = HeiGITRiskPipeline(db_url)
    pipeline.run()
