import abc
import datetime
import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)


class BaseETLPipeline(abc.ABC):
    """Base class for query-on-demand ETL pipelines.

    Pipelines no longer bulk-download and store external data.
    Instead they:
      1. Query the external API on demand.
      2. Optionally cache results in Redis with a TTL.
      3. Log query metadata (what was queried, when, status) to Supabase.
    """

    def __init__(self, db_url: str, data_source_name: str) -> None:
        self.db_url = db_url
        self.data_source_name = data_source_name
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    @abc.abstractmethod
    def extract(self) -> Any:
        """Query the external API and return raw data."""
        ...

    @abc.abstractmethod
    def transform(self, raw_data: Any) -> Any:
        """Transform raw API response into a loggable summary."""
        ...

    @abc.abstractmethod
    def load(self, data: Any) -> Dict[str, int]:
        """Log query metadata to Supabase ingestion_logs.

        Returns {"rows_processed": N, "rows_failed": M}.
        """
        ...

    def run(self) -> None:
        """Execute the query-on-demand pipeline and log metadata to Supabase."""
        log_id = self.log_start()
        try:
            raw = self.extract()
            transformed = self.transform(raw)
            result = self.load(transformed)
            self.log_complete(
                log_id,
                result.get("rows_processed", 0),
                result.get("rows_failed", 0),
            )
            logger.info(
                "Pipeline %s completed: %d rows processed, %d failed",
                self.data_source_name,
                result.get("rows_processed", 0),
                result.get("rows_failed", 0),
            )
        except Exception as exc:
            logger.exception("Pipeline %s failed: %s", self.data_source_name, exc)
            self.log_error(log_id, str(exc))
            raise

    def _get_data_source_id(self, session: Session) -> Optional[uuid.UUID]:
        row = session.execute(
            text("SELECT id FROM data_sources WHERE name = :name"),
            {"name": self.data_source_name},
        ).fetchone()
        return row[0] if row else None

    def log_start(self) -> uuid.UUID:
        log_id = uuid.uuid4()
        with self.SessionLocal() as session:
            ds_id = self._get_data_source_id(session)
            if ds_id:
                session.execute(
                    text(
                        "INSERT INTO ingestion_logs "
                        "(id, data_source_id, started_at, status, rows_processed, rows_failed) "
                        "VALUES (:id, :ds_id, :started_at, 'partial', 0, 0)"
                    ),
                    {
                        "id": str(log_id),
                        "ds_id": str(ds_id),
                        "started_at": datetime.datetime.utcnow(),
                    },
                )
                session.commit()
        return log_id

    def log_complete(
        self, log_id: uuid.UUID, rows_processed: int, rows_failed: int
    ) -> None:
        with self.SessionLocal() as session:
            session.execute(
                text(
                    "UPDATE ingestion_logs SET status='success', completed_at=:completed_at, "
                    "rows_processed=:rp, rows_failed=:rf WHERE id=:id"
                ),
                {
                    "completed_at": datetime.datetime.utcnow(),
                    "rp": rows_processed,
                    "rf": rows_failed,
                    "id": str(log_id),
                },
            )
            session.commit()

    def log_error(self, log_id: uuid.UUID, error_message: str) -> None:
        with self.SessionLocal() as session:
            session.execute(
                text(
                    "UPDATE ingestion_logs SET status='failed', completed_at=:completed_at, "
                    "error_message=:msg WHERE id=:id"
                ),
                {
                    "completed_at": datetime.datetime.utcnow(),
                    "msg": error_message[:2000],
                    "id": str(log_id),
                },
            )
            session.commit()
