import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.ingestion import DataSource, IngestionLog, SyncSchedule
from ..schemas.ingestion import (
    DataSourceCreate,
    DataSourceResponse,
    IngestionLogCreate,
    IngestionLogResponse,
    SyncScheduleCreate,
    SyncScheduleResponse,
)

router = APIRouter(prefix="/data-sources", tags=["data-sources"])


@router.get("/", response_model=List[DataSourceResponse])
def list_sources(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[DataSourceResponse]:
    return db.query(DataSource).offset(skip).limit(limit).all()


@router.get("/{source_id}", response_model=DataSourceResponse)
def get_source(
    source_id: uuid.UUID, db: Session = Depends(get_db)
) -> DataSourceResponse:
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found"
        )
    return source


@router.post(
    "/", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED
)
def create_source(
    source_in: DataSourceCreate, db: Session = Depends(get_db)
) -> DataSourceResponse:
    source = DataSource(**source_in.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.put("/{source_id}", response_model=DataSourceResponse)
def update_source(
    source_id: uuid.UUID,
    source_in: DataSourceCreate,
    db: Session = Depends(get_db),
) -> DataSourceResponse:
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found"
        )
    for key, value in source_in.model_dump(exclude_unset=True).items():
        setattr(source, key, value)
    db.commit()
    db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found"
        )
    db.delete(source)
    db.commit()


router_logs = APIRouter(prefix="/ingestion-logs", tags=["ingestion-logs"])


@router_logs.get("/", response_model=List[IngestionLogResponse])
def list_logs(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[IngestionLogResponse]:
    return db.query(IngestionLog).offset(skip).limit(limit).all()


@router_logs.get("/{log_id}", response_model=IngestionLogResponse)
def get_log(log_id: uuid.UUID, db: Session = Depends(get_db)) -> IngestionLogResponse:
    log = db.query(IngestionLog).filter(IngestionLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion log not found"
        )
    return log


@router_logs.post(
    "/", response_model=IngestionLogResponse, status_code=status.HTTP_201_CREATED
)
def create_log(
    log_in: IngestionLogCreate, db: Session = Depends(get_db)
) -> IngestionLogResponse:
    log = IngestionLog(**log_in.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router_logs.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(log_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    log = db.query(IngestionLog).filter(IngestionLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion log not found"
        )
    db.delete(log)
    db.commit()


router_schedules = APIRouter(prefix="/sync-schedules", tags=["sync-schedules"])


@router_schedules.get("/", response_model=List[SyncScheduleResponse])
def list_schedules(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[SyncScheduleResponse]:
    return db.query(SyncSchedule).offset(skip).limit(limit).all()


@router_schedules.get("/{schedule_id}", response_model=SyncScheduleResponse)
def get_schedule(
    schedule_id: uuid.UUID, db: Session = Depends(get_db)
) -> SyncScheduleResponse:
    schedule = db.query(SyncSchedule).filter(SyncSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sync schedule not found"
        )
    return schedule


@router_schedules.post(
    "/", response_model=SyncScheduleResponse, status_code=status.HTTP_201_CREATED
)
def create_schedule(
    schedule_in: SyncScheduleCreate, db: Session = Depends(get_db)
) -> SyncScheduleResponse:
    schedule = SyncSchedule(**schedule_in.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router_schedules.put("/{schedule_id}", response_model=SyncScheduleResponse)
def update_schedule(
    schedule_id: uuid.UUID,
    schedule_in: SyncScheduleCreate,
    db: Session = Depends(get_db),
) -> SyncScheduleResponse:
    schedule = db.query(SyncSchedule).filter(SyncSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sync schedule not found"
        )
    for key, value in schedule_in.model_dump(exclude_unset=True).items():
        setattr(schedule, key, value)
    db.commit()
    db.refresh(schedule)
    return schedule


@router_schedules.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    schedule = db.query(SyncSchedule).filter(SyncSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sync schedule not found"
        )
    db.delete(schedule)
    db.commit()
