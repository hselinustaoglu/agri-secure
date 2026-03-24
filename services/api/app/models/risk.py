import uuid
import enum

from sqlalchemy import Column, Date, Enum, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class ServiceType(str, enum.Enum):
    health = "health"
    education = "education"
    market = "market"


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_area_id = Column(UUID(as_uuid=True), nullable=True)
    indicator_type = Column(String(100), nullable=True)
    value = Column(Float, nullable=True)
    score = Column(Float, nullable=True)
    assessment_date = Column(Date, nullable=False)
    source = Column(String(100), nullable=True)


class VulnerabilityIndicator(Base):
    __tablename__ = "vulnerability_indicators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_area_id = Column(UUID(as_uuid=True), nullable=True)
    demographic_score = Column(Float, nullable=True)
    environmental_score = Column(Float, nullable=True)
    infrastructure_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)


class FloodExposure(Base):
    __tablename__ = "flood_exposures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_area_id = Column(UUID(as_uuid=True), nullable=True)
    exposure_level = Column(String(50), nullable=True)
    affected_population = Column(Integer, nullable=True)
    area_km2 = Column(Float, nullable=True)
    assessment_date = Column(Date, nullable=False)


class AccessibilityScore(Base):
    __tablename__ = "accessibility_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_area_id = Column(UUID(as_uuid=True), nullable=True)
    service_type = Column(Enum(ServiceType), nullable=False)
    travel_time_minutes = Column(Float, nullable=True)
    population_covered = Column(Integer, nullable=True)
