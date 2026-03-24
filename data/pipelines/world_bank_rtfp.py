"""World Bank Real-Time Food Prices (RTFP) pipeline."""

import logging
import os
import uuid
from typing import Any, Dict, List

import httpx
from sqlalchemy import text

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

CATALOG_URL = "https://microdata.worldbank.org/index.php/api/catalog/4483"


class WorldBankRTFPPipeline(BaseETLPipeline):
    """Downloads monthly food price estimates from World Bank RTFP."""

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "World Bank RTFP")
        self.target_countries = os.getenv("TARGET_COUNTRIES", "KEN,ETH,NGA").split(",")

    def extract(self) -> Any:
        logger.info("Fetching World Bank RTFP catalog from %s", CATALOG_URL)
        with httpx.Client(timeout=60) as client:
            resp = client.get(CATALOG_URL, params={"format": "json"})
            resp.raise_for_status()
            return resp.json()

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        study = raw_data if isinstance(raw_data, dict) else {}
        logger.info(
            "Transforming World Bank RTFP catalog: %s", study.get("id", "unknown")
        )
        return records

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        if not data:
            logger.warning("No RTFP price records to load")
            return {"rows_processed": 0, "rows_failed": 0}
        rows_processed = 0
        rows_failed = 0
        with self.SessionLocal() as session:
            for record in data:
                try:
                    session.execute(
                        text(
                            "INSERT INTO market_prices "
                            "(id, market_id, crop_id, price, currency, unit, price_date, source) "
                            "VALUES (:id, :market_id, :crop_id, :price, :currency, :unit, :price_date, 'world_bank') "
                            "ON CONFLICT DO NOTHING"
                        ),
                        {
                            "id": str(uuid.uuid4()),
                            "market_id": record.get("market_id"),
                            "crop_id": record.get("crop_id"),
                            "price": record.get("price"),
                            "currency": record.get("currency", "USD"),
                            "unit": record.get("unit"),
                            "price_date": record.get("price_date"),
                        },
                    )
                    rows_processed += 1
                except Exception as exc:
                    logger.error("Failed to insert RTFP record: %s", exc)
                    rows_failed += 1
            session.commit()
        return {"rows_processed": rows_processed, "rows_failed": rows_failed}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = WorldBankRTFPPipeline(db_url)
    pipeline.run()
