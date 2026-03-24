import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from ..models.climate import RainfallSource


class WeatherDataBase(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    precipitation: Optional[float] = None
    forecast_date: datetime.datetime
    source: Optional[str] = None


class WeatherDataCreate(WeatherDataBase):
    pass


class WeatherDataResponse(WeatherDataBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class RainfallRecordBase(BaseModel):
    period_start: datetime.date
    period_end: datetime.date
    rainfall_mm: float
    anomaly_pct: Optional[float] = None
    source: RainfallSource = RainfallSource.chirps


class RainfallRecordCreate(RainfallRecordBase):
    region_id: Optional[uuid.UUID] = None


class RainfallRecordResponse(RainfallRecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    region_id: Optional[uuid.UUID] = None


class SoilMoistureBase(BaseModel):
    depth_cm: Optional[int] = None
    moisture_pct: Optional[float] = None
    measurement_date: datetime.datetime
    source: Optional[str] = None


class SoilMoistureCreate(SoilMoistureBase):
    pass


class SoilMoistureResponse(SoilMoistureBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
