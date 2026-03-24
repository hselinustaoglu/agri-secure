import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FarmerBase(BaseModel):
    name: str
    phone: Optional[str] = None
    language: str = "en"


class FarmerCreate(FarmerBase):
    pass


class FarmerResponse(FarmerBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime


class FarmBase(BaseModel):
    name: str
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None


class FarmCreate(FarmBase):
    farmer_id: uuid.UUID


class FarmResponse(FarmBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    farmer_id: uuid.UUID


class CropBase(BaseModel):
    name: str
    category: Optional[str] = None
    growing_season: Optional[str] = None


class CropCreate(CropBase):
    pass


class CropResponse(CropBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
