import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.food_security import FoodSecurityIndicator
from ..schemas.food_security import (
    FoodSecurityIndicatorCreate,
    FoodSecurityIndicatorResponse,
)

router = APIRouter(prefix="/food-security", tags=["food-security"])


@router.get("/", response_model=List[FoodSecurityIndicatorResponse])
def list_indicators(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[FoodSecurityIndicatorResponse]:
    return db.query(FoodSecurityIndicator).offset(skip).limit(limit).all()


@router.get("/{indicator_id}", response_model=FoodSecurityIndicatorResponse)
def get_indicator(
    indicator_id: uuid.UUID, db: Session = Depends(get_db)
) -> FoodSecurityIndicatorResponse:
    indicator = (
        db.query(FoodSecurityIndicator)
        .filter(FoodSecurityIndicator.id == indicator_id)
        .first()
    )
    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food security indicator not found",
        )
    return indicator


@router.post(
    "/",
    response_model=FoodSecurityIndicatorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_indicator(
    indicator_in: FoodSecurityIndicatorCreate, db: Session = Depends(get_db)
) -> FoodSecurityIndicatorResponse:
    indicator = FoodSecurityIndicator(**indicator_in.model_dump())
    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    return indicator


@router.put("/{indicator_id}", response_model=FoodSecurityIndicatorResponse)
def update_indicator(
    indicator_id: uuid.UUID,
    indicator_in: FoodSecurityIndicatorCreate,
    db: Session = Depends(get_db),
) -> FoodSecurityIndicatorResponse:
    indicator = (
        db.query(FoodSecurityIndicator)
        .filter(FoodSecurityIndicator.id == indicator_id)
        .first()
    )
    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food security indicator not found",
        )
    for key, value in indicator_in.model_dump(exclude_unset=True).items():
        setattr(indicator, key, value)
    db.commit()
    db.refresh(indicator)
    return indicator


@router.delete("/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator(indicator_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    indicator = (
        db.query(FoodSecurityIndicator)
        .filter(FoodSecurityIndicator.id == indicator_id)
        .first()
    )
    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food security indicator not found",
        )
    db.delete(indicator)
    db.commit()
