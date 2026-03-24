import datetime
import enum
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class AlertType(str, enum.Enum):
    drought = "drought"
    flood = "flood"
    pest = "pest"
    price_spike = "price_spike"


class AlertSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AlertAction(str, enum.Enum):
    sms = "sms"
    email = "email"
    whatsapp = "whatsapp"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.medium)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    affected_area = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    notifications = relationship("AlertNotification", back_populates="alert")


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(255), nullable=False)
    condition_json = Column(Text, nullable=True)
    action = Column(Enum(AlertAction), nullable=False)
    active = Column(Boolean, default=True)


class AlertNotification(Base):
    __tablename__ = "alert_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=False)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=True)
    channel = Column(String(50), nullable=True)
    status = Column(String(50), nullable=True)
    sent_at = Column(DateTime, nullable=True)

    alert = relationship("Alert", back_populates="notifications")
