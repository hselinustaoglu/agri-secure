import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from ..models.food_security import FoodSecurityIndicatorType


class FoodSecurityIndicatorBase(BaseModel):
    indicator_type: FoodSecurityIndicatorType
    value: Optional[float] = None
    classification: Optional[str] = None
    period_start: datetime.date
    period_end: datetime.date
    source: Optional[str] = None


class FoodSecurityIndicatorCreate(FoodSecurityIndicatorBase):
    region_id: Optional[uuid.UUID] = None


class FoodSecurityIndicatorResponse(FoodSecurityIndicatorBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    region_id: Optional[uuid.UUID] = None
