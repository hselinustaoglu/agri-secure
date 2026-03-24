import datetime
import enum
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class PriceSource(str, enum.Enum):
    manual = "manual"
    world_bank = "world_bank"
    wfp = "wfp"
    fao = "fao"


class Market(Base):
    __tablename__ = "markets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    country_code = Column(String(10), nullable=False)
    admin_level_1 = Column(String(255), nullable=True)
    admin_level_2 = Column(String(255), nullable=True)

    prices = relationship("MarketPrice", back_populates="market")
    price_alerts = relationship("PriceAlert", back_populates="market")


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=False)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    unit = Column(String(50), nullable=True)
    price_date = Column(Date, nullable=False)
    source = Column(Enum(PriceSource), default=PriceSource.manual)

    market = relationship("Market", back_populates="prices")
    crop = relationship("Crop", back_populates="market_prices")


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=True)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=True)
    alert_type = Column(String(100), nullable=True)
    threshold = Column(Float, nullable=True)
    message = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    market = relationship("Market", back_populates="price_alerts")
