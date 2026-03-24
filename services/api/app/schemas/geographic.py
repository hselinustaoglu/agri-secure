import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RegionBase(BaseModel):
    name: str
    country_code: str
    admin_level: int


class RegionCreate(RegionBase):
    parent_id: Optional[uuid.UUID] = None


class RegionResponse(RegionBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None


class LivelihoodZoneBase(BaseModel):
    name: str
    zone_type: Optional[str] = None
    description: Optional[str] = None


class LivelihoodZoneCreate(LivelihoodZoneBase):
    pass


class LivelihoodZoneResponse(LivelihoodZoneBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
