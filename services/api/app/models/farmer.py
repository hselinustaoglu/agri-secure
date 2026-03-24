import datetime
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), unique=True, nullable=True)
    language = Column(String(10), default="en")
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    farms = relationship("Farm", back_populates="farmer")
    farmer_crops = relationship("FarmerCrop", back_populates="farmer")


class Farm(Base):
    __tablename__ = "farms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    name = Column(String(255), nullable=False)
    area_hectares = Column(Float, nullable=True)
    location = Column(Geometry("POLYGON", srid=4326), nullable=True)
    soil_type = Column(String(100), nullable=True)

    farmer = relationship("Farmer", back_populates="farms")


class Crop(Base):
    __tablename__ = "crops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    category = Column(String(100), nullable=True)
    growing_season = Column(String(100), nullable=True)

    farmer_crops = relationship("FarmerCrop", back_populates="crop")
    market_prices = relationship("MarketPrice", back_populates="crop")


class FarmerCrop(Base):
    __tablename__ = "farmer_crops"

    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), primary_key=True)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), primary_key=True)
    planted_date = Column(Date, nullable=True)
    harvest_date = Column(Date, nullable=True)
    area_hectares = Column(Float, nullable=True)

    farmer = relationship("Farmer", back_populates="farmer_crops")
    crop = relationship("Crop", back_populates="farmer_crops")
