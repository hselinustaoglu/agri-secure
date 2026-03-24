import uuid
import enum

from sqlalchemy import Column, Date, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class FoodSecurityIndicatorType(str, enum.Enum):
    ipc_phase = "ipc_phase"
    fcs = "fcs"
    hdds = "hdds"
    rcsi = "rcsi"


class FoodSecurityIndicator(Base):
    __tablename__ = "food_security_indicators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=True)
    indicator_type = Column(Enum(FoodSecurityIndicatorType), nullable=False)
    value = Column(Float, nullable=True)
    classification = Column(String(100), nullable=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    source = Column(String(100), nullable=True)
