"""WFP food prices pipeline."""

import logging
import os
import uuid
from typing import Any, Dict, List

import httpx
from sqlalchemy import text

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

API_URL = "https://api.hungermapdata.org/api/v2/country/all/marketprice"


class WFPPricesPipeline(BaseETLPipeline):
    """Downloads food prices from WFP HungerMap API."""

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "WFP Prices")
        self.target_countries = os.getenv("TARGET_COUNTRIES", "KEN,ETH,NGA").split(",")

    def extract(self) -> Any:
        logger.info("Fetching WFP market prices from %s", API_URL)
        with httpx.Client(timeout=60) as client:
            resp = client.get(API_URL)
            resp.raise_for_status()
            return resp.json()

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        items = raw_data if isinstance(raw_data, list) else raw_data.get("data", [])
        for item in items:
            country = item.get("country_iso3", "")
            if country not in self.target_countries:
                continue
            for price_entry in item.get("prices", []):
                records.append(
                    {
                        "market_name": item.get("market_name", "Unknown"),
                        "commodity": price_entry.get("commodity", ""),
                        "price": price_entry.get("price"),
                        "currency": price_entry.get("currency", "USD"),
                        "unit": price_entry.get("unit"),
                        "price_date": price_entry.get("date"),
                        "country_code": country,
                    }
                )
        logger.info("Transformed %d WFP price records", len(records))
        return records

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        if not data:
            logger.warning("No WFP price records to load")
            return {"rows_processed": 0, "rows_failed": 0}
        rows_processed = 0
        rows_failed = 0
        with self.SessionLocal() as session:
            for record in data:
                try:
                    market_row = session.execute(
                        text(
                            "SELECT id FROM markets WHERE name = :name "
                            "AND country_code = :cc LIMIT 1"
                        ),
                        {
                            "name": record["market_name"],
                            "cc": record["country_code"],
                        },
                    ).fetchone()
                    if not market_row:
                        rows_failed += 1
                        continue
                    crop_row = session.execute(
                        text("SELECT id FROM crops WHERE name = :name LIMIT 1"),
                        {"name": record["commodity"]},
                    ).fetchone()
                    if not crop_row:
                        rows_failed += 1
                        continue
                    session.execute(
                        text(
                            "INSERT INTO market_prices "
                            "(id, market_id, crop_id, price, currency, unit, price_date, source) "
                            "VALUES (:id, :market_id, :crop_id, :price, :currency, :unit, :price_date, 'wfp') "
                            "ON CONFLICT DO NOTHING"
                        ),
                        {
                            "id": str(uuid.uuid4()),
                            "market_id": str(market_row[0]),
                            "crop_id": str(crop_row[0]),
                            "price": record["price"],
                            "currency": record["currency"],
                            "unit": record["unit"],
                            "price_date": record["price_date"],
                        },
                    )
                    rows_processed += 1
                except Exception as exc:
                    logger.error("Failed to insert WFP record: %s", exc)
                    rows_failed += 1
            session.commit()
        return {"rows_processed": rows_processed, "rows_failed": rows_failed}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = WFPPricesPipeline(db_url)
    pipeline.run()
