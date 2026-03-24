import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.alert import Alert, AlertNotification, AlertRule
from ..schemas.alert import (
    AlertCreate,
    AlertNotificationCreate,
    AlertNotificationResponse,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[AlertResponse]:
    return db.query(Alert).offset(skip).limit(limit).all()


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: uuid.UUID, db: Session = Depends(get_db)) -> AlertResponse:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found"
        )
    return alert


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(alert_in: AlertCreate, db: Session = Depends(get_db)) -> AlertResponse:
    alert = Alert(**alert_in.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: uuid.UUID, alert_in: AlertCreate, db: Session = Depends(get_db)
) -> AlertResponse:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found"
        )
    for key, value in alert_in.model_dump(exclude_unset=True).items():
        setattr(alert, key, value)
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found"
        )
    db.delete(alert)
    db.commit()


router_rules = APIRouter(prefix="/alert-rules", tags=["alert-rules"])


@router_rules.get("/", response_model=List[AlertRuleResponse])
def list_rules(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[AlertRuleResponse]:
    return db.query(AlertRule).offset(skip).limit(limit).all()


@router_rules.get("/{rule_id}", response_model=AlertRuleResponse)
def get_rule(rule_id: uuid.UUID, db: Session = Depends(get_db)) -> AlertRuleResponse:
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found"
        )
    return rule


@router_rules.post(
    "/", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED
)
def create_rule(
    rule_in: AlertRuleCreate, db: Session = Depends(get_db)
) -> AlertRuleResponse:
    rule = AlertRule(**rule_in.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router_rules.put("/{rule_id}", response_model=AlertRuleResponse)
def update_rule(
    rule_id: uuid.UUID, rule_in: AlertRuleCreate, db: Session = Depends(get_db)
) -> AlertRuleResponse:
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found"
        )
    for key, value in rule_in.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return rule


@router_rules.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found"
        )
    db.delete(rule)
    db.commit()


router_notifications = APIRouter(
    prefix="/alert-notifications", tags=["alert-notifications"]
)


@router_notifications.get("/", response_model=List[AlertNotificationResponse])
def list_notifications(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[AlertNotificationResponse]:
    return db.query(AlertNotification).offset(skip).limit(limit).all()


@router_notifications.get("/{notif_id}", response_model=AlertNotificationResponse)
def get_notification(
    notif_id: uuid.UUID, db: Session = Depends(get_db)
) -> AlertNotificationResponse:
    notif = db.query(AlertNotification).filter(AlertNotification.id == notif_id).first()
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    return notif


@router_notifications.post(
    "/", response_model=AlertNotificationResponse, status_code=status.HTTP_201_CREATED
)
def create_notification(
    notif_in: AlertNotificationCreate, db: Session = Depends(get_db)
) -> AlertNotificationResponse:
    notif = AlertNotification(**notif_in.model_dump())
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


@router_notifications.delete("/{notif_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notif_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    notif = db.query(AlertNotification).filter(AlertNotification.id == notif_id).first()
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    db.delete(notif)
    db.commit()
