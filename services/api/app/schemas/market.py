import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from ..models.market import PriceSource


class MarketBase(BaseModel):
    name: str
    country_code: str
    admin_level_1: Optional[str] = None
    admin_level_2: Optional[str] = None


class MarketCreate(MarketBase):
    pass


class MarketResponse(MarketBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class MarketPriceBase(BaseModel):
    price: float
    currency: str = "USD"
    unit: Optional[str] = None
    price_date: datetime.date
    source: PriceSource = PriceSource.manual


class MarketPriceCreate(MarketPriceBase):
    market_id: uuid.UUID
    crop_id: uuid.UUID


class MarketPriceResponse(MarketPriceBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    market_id: uuid.UUID
    crop_id: uuid.UUID


class PriceAlertBase(BaseModel):
    alert_type: Optional[str] = None
    threshold: Optional[float] = None
    message: Optional[str] = None


class PriceAlertCreate(PriceAlertBase):
    market_id: Optional[uuid.UUID] = None
    crop_id: Optional[uuid.UUID] = None


class PriceAlertResponse(PriceAlertBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime.datetime
