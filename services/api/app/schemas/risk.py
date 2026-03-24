import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from ..models.risk import ServiceType


class RiskAssessmentBase(BaseModel):
    indicator_type: Optional[str] = None
    value: Optional[float] = None
    score: Optional[float] = None
    assessment_date: datetime.date
    source: Optional[str] = None


class RiskAssessmentCreate(RiskAssessmentBase):
    admin_area_id: Optional[uuid.UUID] = None


class RiskAssessmentResponse(RiskAssessmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    admin_area_id: Optional[uuid.UUID] = None


class VulnerabilityIndicatorBase(BaseModel):
    demographic_score: Optional[float] = None
    environmental_score: Optional[float] = None
    infrastructure_score: Optional[float] = None
    overall_score: Optional[float] = None


class VulnerabilityIndicatorCreate(VulnerabilityIndicatorBase):
    admin_area_id: Optional[uuid.UUID] = None


class VulnerabilityIndicatorResponse(VulnerabilityIndicatorBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    admin_area_id: Optional[uuid.UUID] = None


class AccessibilityScoreBase(BaseModel):
    service_type: ServiceType
    travel_time_minutes: Optional[float] = None
    population_covered: Optional[int] = None


class AccessibilityScoreCreate(AccessibilityScoreBase):
    admin_area_id: Optional[uuid.UUID] = None


class AccessibilityScoreResponse(AccessibilityScoreBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    admin_area_id: Optional[uuid.UUID] = None
