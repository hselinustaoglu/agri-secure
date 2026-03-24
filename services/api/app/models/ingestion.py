import datetime
import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class IngestionStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    partial = "partial"


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    url = Column(String(1000), nullable=True)
    source_type = Column(String(50), nullable=True)
    refresh_interval = Column(Integer, nullable=True)
    last_sync = Column(DateTime, nullable=True)
    status = Column(String(50), default="active")
    config_json = Column(Text, nullable=True)

    ingestion_logs = relationship("IngestionLog", back_populates="data_source")
    sync_schedules = relationship("SyncSchedule", back_populates="data_source")


class IngestionLog(Base):
    __tablename__ = "ingestion_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_source_id = Column(
        UUID(as_uuid=True), ForeignKey("data_sources.id"), nullable=False
    )
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(Enum(IngestionStatus), nullable=False)
    rows_processed = Column(Integer, default=0)
    rows_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    data_source = relationship("DataSource", back_populates="ingestion_logs")


class SyncSchedule(Base):
    __tablename__ = "sync_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_source_id = Column(
        UUID(as_uuid=True), ForeignKey("data_sources.id"), nullable=False
    )
    cron_expression = Column(String(100), nullable=False)
    next_run = Column(DateTime, nullable=True)
    last_success = Column(DateTime, nullable=True)
    enabled = Column(Boolean, default=True)

    data_source = relationship("DataSource", back_populates="sync_schedules")
