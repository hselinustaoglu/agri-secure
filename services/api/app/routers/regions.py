import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.geographic import LivelihoodZone, Region
from ..schemas.geographic import (
    LivelihoodZoneCreate,
    LivelihoodZoneResponse,
    RegionCreate,
    RegionResponse,
)

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("/", response_model=List[RegionResponse])
def list_regions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[RegionResponse]:
    return db.query(Region).offset(skip).limit(limit).all()


@router.get("/{region_id}", response_model=RegionResponse)
def get_region(region_id: uuid.UUID, db: Session = Depends(get_db)) -> RegionResponse:
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Region not found"
        )
    return region


@router.post("/", response_model=RegionResponse, status_code=status.HTTP_201_CREATED)
def create_region(
    region_in: RegionCreate, db: Session = Depends(get_db)
) -> RegionResponse:
    region = Region(**region_in.model_dump())
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


@router.put("/{region_id}", response_model=RegionResponse)
def update_region(
    region_id: uuid.UUID, region_in: RegionCreate, db: Session = Depends(get_db)
) -> RegionResponse:
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Region not found"
        )
    for key, value in region_in.model_dump(exclude_unset=True).items():
        setattr(region, key, value)
    db.commit()
    db.refresh(region)
    return region


@router.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_region(region_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Region not found"
        )
    db.delete(region)
    db.commit()


router_zones = APIRouter(prefix="/livelihood-zones", tags=["livelihood-zones"])


@router_zones.get("/", response_model=List[LivelihoodZoneResponse])
def list_zones(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[LivelihoodZoneResponse]:
    return db.query(LivelihoodZone).offset(skip).limit(limit).all()


@router_zones.get("/{zone_id}", response_model=LivelihoodZoneResponse)
def get_zone(
    zone_id: uuid.UUID, db: Session = Depends(get_db)
) -> LivelihoodZoneResponse:
    zone = db.query(LivelihoodZone).filter(LivelihoodZone.id == zone_id).first()
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Livelihood zone not found"
        )
    return zone


@router_zones.post(
    "/", response_model=LivelihoodZoneResponse, status_code=status.HTTP_201_CREATED
)
def create_zone(
    zone_in: LivelihoodZoneCreate, db: Session = Depends(get_db)
) -> LivelihoodZoneResponse:
    zone = LivelihoodZone(**zone_in.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router_zones.put("/{zone_id}", response_model=LivelihoodZoneResponse)
def update_zone(
    zone_id: uuid.UUID,
    zone_in: LivelihoodZoneCreate,
    db: Session = Depends(get_db),
) -> LivelihoodZoneResponse:
    zone = db.query(LivelihoodZone).filter(LivelihoodZone.id == zone_id).first()
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Livelihood zone not found"
        )
    for key, value in zone_in.model_dump(exclude_unset=True).items():
        setattr(zone, key, value)
    db.commit()
    db.refresh(zone)
    return zone


@router_zones.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(zone_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    zone = db.query(LivelihoodZone).filter(LivelihoodZone.id == zone_id).first()
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Livelihood zone not found"
        )
    db.delete(zone)
    db.commit()
