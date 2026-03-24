"""CHIRPS rainfall TIF files pipeline."""

import io
import logging
import os
import uuid
from typing import Any, Dict, List

import httpx
from sqlalchemy import text

from .base import BaseETLPipeline

logger = logging.getLogger(__name__)

CHIRPS_BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/"


class CHIRPSPipeline(BaseETLPipeline):
    """Downloads and processes CHIRPS monthly rainfall TIF files."""

    def __init__(self, db_url: str) -> None:
        super().__init__(db_url, "CHIRPS")
        self.target_countries = os.getenv("TARGET_COUNTRIES", "KEN,ETH,NGA").split(",")

    def _get_latest_filename(self) -> str:
        import datetime

        now = datetime.datetime.utcnow()
        year = now.year
        month = now.month - 1 if now.month > 1 else 12
        if now.month == 1:
            year -= 1
        return f"chirps-v2.0.{year}.{month:02d}.tif.gz"

    def extract(self) -> Any:
        filename = self._get_latest_filename()
        url = f"{CHIRPS_BASE_URL}{filename}"
        logger.info("Downloading CHIRPS file: %s", url)
        with httpx.Client(timeout=300) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return {"filename": filename, "content": resp.content}

    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        try:
            import gzip
            import rasterio

            content = raw_data["content"]
            with gzip.open(io.BytesIO(content)) as gz_file:
                tif_data = gz_file.read()
            with rasterio.open(io.BytesIO(tif_data)) as dataset:
                band = dataset.read(1)
                valid = (
                    band[band != dataset.nodata] if dataset.nodata else band.flatten()
                )
                mean_rainfall = float(valid.mean()) if len(valid) > 0 else 0.0
                records.append(
                    {
                        "filename": raw_data["filename"],
                        "mean_rainfall_mm": mean_rainfall,
                        "country_code": "GLOBAL",
                    }
                )
            logger.info("Processed CHIRPS file, mean rainfall: %.2f mm", mean_rainfall)
        except Exception as exc:
            logger.error("Failed to process CHIRPS TIF: %s", exc)
        return records

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        if not data:
            logger.warning("No CHIRPS records to load")
            return {"rows_processed": 0, "rows_failed": 0}
        import datetime

        rows_processed = 0
        rows_failed = 0
        now = datetime.datetime.utcnow()
        period_end = now.replace(day=1) - datetime.timedelta(days=1)
        period_start = period_end.replace(day=1)
        with self.SessionLocal() as session:
            for record in data:
                try:
                    session.execute(
                        text(
                            "INSERT INTO rainfall_records "
                            "(id, period_start, period_end, rainfall_mm, source) "
                            "VALUES (:id, :period_start, :period_end, :rainfall_mm, 'chirps') "
                            "ON CONFLICT DO NOTHING"
                        ),
                        {
                            "id": str(uuid.uuid4()),
                            "period_start": period_start.date(),
                            "period_end": period_end.date(),
                            "rainfall_mm": record["mean_rainfall_mm"],
                        },
                    )
                    rows_processed += 1
                except Exception as exc:
                    logger.error("Failed to insert CHIRPS record: %s", exc)
                    rows_failed += 1
            session.commit()
        return {"rows_processed": rows_processed, "rows_failed": rows_failed}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    pipeline = CHIRPSPipeline(db_url)
    pipeline.run()
