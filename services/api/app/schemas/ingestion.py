import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from ..models.ingestion import IngestionStatus


class DataSourceBase(BaseModel):
    name: str
    url: Optional[str] = None
    source_type: Optional[str] = None
    refresh_interval: Optional[int] = None
    status: str = "active"
    config_json: Optional[str] = None


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceResponse(DataSourceBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    last_sync: Optional[datetime.datetime] = None


class IngestionLogBase(BaseModel):
    status: IngestionStatus
    rows_processed: int = 0
    rows_failed: int = 0
    error_message: Optional[str] = None


class IngestionLogCreate(IngestionLogBase):
    data_source_id: uuid.UUID


class IngestionLogResponse(IngestionLogBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    data_source_id: uuid.UUID
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None


class SyncScheduleBase(BaseModel):
    cron_expression: str
    enabled: bool = True


class SyncScheduleCreate(SyncScheduleBase):
    data_source_id: uuid.UUID


class SyncScheduleResponse(SyncScheduleBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    data_source_id: uuid.UUID
    next_run: Optional[datetime.datetime] = None
    last_success: Optional[datetime.datetime] = None
