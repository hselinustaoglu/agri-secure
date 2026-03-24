import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from ..models.alert import AlertAction, AlertSeverity, AlertType


class AlertBase(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity = AlertSeverity.medium
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime.datetime


class AlertRuleBase(BaseModel):
    rule_name: str
    condition_json: Optional[str] = None
    action: AlertAction
    active: bool = True


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleResponse(AlertRuleBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class AlertNotificationBase(BaseModel):
    channel: Optional[str] = None
    status: Optional[str] = None
    sent_at: Optional[datetime.datetime] = None


class AlertNotificationCreate(AlertNotificationBase):
    alert_id: uuid.UUID
    farmer_id: Optional[uuid.UUID] = None


class AlertNotificationResponse(AlertNotificationBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    alert_id: uuid.UUID
    farmer_id: Optional[uuid.UUID] = None
