import uuid
import enum

from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, DateTime, Enum, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class RainfallSource(str, enum.Enum):
    chirps = "chirps"
    station = "station"


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    precipitation = Column(Float, nullable=True)
    forecast_date = Column(DateTime, nullable=False)
    source = Column(String(100), nullable=True)


class RainfallRecord(Base):
    __tablename__ = "rainfall_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id = Column(UUID(as_uuid=True), nullable=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    rainfall_mm = Column(Float, nullable=False)
    anomaly_pct = Column(Float, nullable=True)
    source = Column(Enum(RainfallSource), default=RainfallSource.chirps)


class SoilMoisture(Base):
    __tablename__ = "soil_moisture"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    depth_cm = Column(Integer, nullable=True)
    moisture_pct = Column(Float, nullable=True)
    measurement_date = Column(DateTime, nullable=False)
    source = Column(String(100), nullable=True)
