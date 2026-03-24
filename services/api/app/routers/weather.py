import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.climate import RainfallRecord, SoilMoisture, WeatherData
from ..schemas.climate import (
    RainfallRecordCreate,
    RainfallRecordResponse,
    SoilMoistureCreate,
    SoilMoistureResponse,
    WeatherDataCreate,
    WeatherDataResponse,
)

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/", response_model=List[WeatherDataResponse])
def list_weather(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[WeatherDataResponse]:
    return db.query(WeatherData).offset(skip).limit(limit).all()


@router.get("/{weather_id}", response_model=WeatherDataResponse)
def get_weather(
    weather_id: uuid.UUID, db: Session = Depends(get_db)
) -> WeatherDataResponse:
    record = db.query(WeatherData).filter(WeatherData.id == weather_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Weather record not found"
        )
    return record


@router.post(
    "/", response_model=WeatherDataResponse, status_code=status.HTTP_201_CREATED
)
def create_weather(
    weather_in: WeatherDataCreate, db: Session = Depends(get_db)
) -> WeatherDataResponse:
    record = WeatherData(**weather_in.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{weather_id}", response_model=WeatherDataResponse)
def update_weather(
    weather_id: uuid.UUID,
    weather_in: WeatherDataCreate,
    db: Session = Depends(get_db),
) -> WeatherDataResponse:
    record = db.query(WeatherData).filter(WeatherData.id == weather_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Weather record not found"
        )
    for key, value in weather_in.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{weather_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weather(weather_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    record = db.query(WeatherData).filter(WeatherData.id == weather_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Weather record not found"
        )
    db.delete(record)
    db.commit()


router_rainfall = APIRouter(prefix="/rainfall", tags=["rainfall"])


@router_rainfall.get("/", response_model=List[RainfallRecordResponse])
def list_rainfall(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[RainfallRecordResponse]:
    return db.query(RainfallRecord).offset(skip).limit(limit).all()


@router_rainfall.get("/{record_id}", response_model=RainfallRecordResponse)
def get_rainfall(
    record_id: uuid.UUID, db: Session = Depends(get_db)
) -> RainfallRecordResponse:
    record = db.query(RainfallRecord).filter(RainfallRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rainfall record not found"
        )
    return record


@router_rainfall.post(
    "/", response_model=RainfallRecordResponse, status_code=status.HTTP_201_CREATED
)
def create_rainfall(
    record_in: RainfallRecordCreate, db: Session = Depends(get_db)
) -> RainfallRecordResponse:
    record = RainfallRecord(**record_in.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router_rainfall.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rainfall(record_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    record = db.query(RainfallRecord).filter(RainfallRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rainfall record not found"
        )
    db.delete(record)
    db.commit()


router_soil = APIRouter(prefix="/soil-moisture", tags=["soil-moisture"])


@router_soil.get("/", response_model=List[SoilMoistureResponse])
def list_soil(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[SoilMoistureResponse]:
    return db.query(SoilMoisture).offset(skip).limit(limit).all()


@router_soil.get("/{record_id}", response_model=SoilMoistureResponse)
def get_soil(
    record_id: uuid.UUID, db: Session = Depends(get_db)
) -> SoilMoistureResponse:
    record = db.query(SoilMoisture).filter(SoilMoisture.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Soil moisture record not found",
        )
    return record


@router_soil.post(
    "/", response_model=SoilMoistureResponse, status_code=status.HTTP_201_CREATED
)
def create_soil(
    record_in: SoilMoistureCreate, db: Session = Depends(get_db)
) -> SoilMoistureResponse:
    record = SoilMoisture(**record_in.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router_soil.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_soil(record_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    record = db.query(SoilMoisture).filter(SoilMoisture.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Soil moisture record not found",
        )
    db.delete(record)
    db.commit()
