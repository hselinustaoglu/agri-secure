import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.farmer import Crop, Farm, Farmer
from ..schemas.farmer import (
    CropCreate,
    CropResponse,
    FarmCreate,
    FarmResponse,
    FarmerCreate,
    FarmerResponse,
)

router = APIRouter(prefix="/farmers", tags=["farmers"])


@router.get("/", response_model=List[FarmerResponse])
def list_farmers(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[FarmerResponse]:
    return db.query(Farmer).offset(skip).limit(limit).all()


@router.get("/{farmer_id}", response_model=FarmerResponse)
def get_farmer(farmer_id: uuid.UUID, db: Session = Depends(get_db)) -> FarmerResponse:
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found"
        )
    return farmer


@router.post("/", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
def create_farmer(
    farmer_in: FarmerCreate, db: Session = Depends(get_db)
) -> FarmerResponse:
    farmer = Farmer(**farmer_in.model_dump())
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return farmer


@router.put("/{farmer_id}", response_model=FarmerResponse)
def update_farmer(
    farmer_id: uuid.UUID, farmer_in: FarmerCreate, db: Session = Depends(get_db)
) -> FarmerResponse:
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found"
        )
    for key, value in farmer_in.model_dump(exclude_unset=True).items():
        setattr(farmer, key, value)
    db.commit()
    db.refresh(farmer)
    return farmer


@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farmer(farmer_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found"
        )
    db.delete(farmer)
    db.commit()


router_farms = APIRouter(prefix="/farms", tags=["farms"])


@router_farms.get("/", response_model=List[FarmResponse])
def list_farms(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[FarmResponse]:
    return db.query(Farm).offset(skip).limit(limit).all()


@router_farms.get("/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: uuid.UUID, db: Session = Depends(get_db)) -> FarmResponse:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found"
        )
    return farm


@router_farms.post(
    "/", response_model=FarmResponse, status_code=status.HTTP_201_CREATED
)
def create_farm(farm_in: FarmCreate, db: Session = Depends(get_db)) -> FarmResponse:
    farm = Farm(**farm_in.model_dump())
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router_farms.put("/{farm_id}", response_model=FarmResponse)
def update_farm(
    farm_id: uuid.UUID, farm_in: FarmCreate, db: Session = Depends(get_db)
) -> FarmResponse:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found"
        )
    for key, value in farm_in.model_dump(exclude_unset=True).items():
        setattr(farm, key, value)
    db.commit()
    db.refresh(farm)
    return farm


@router_farms.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(farm_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found"
        )
    db.delete(farm)
    db.commit()


router_crops = APIRouter(prefix="/crops", tags=["crops"])


@router_crops.get("/", response_model=List[CropResponse])
def list_crops(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[CropResponse]:
    return db.query(Crop).offset(skip).limit(limit).all()


@router_crops.get("/{crop_id}", response_model=CropResponse)
def get_crop(crop_id: uuid.UUID, db: Session = Depends(get_db)) -> CropResponse:
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
        )
    return crop


@router_crops.post(
    "/", response_model=CropResponse, status_code=status.HTTP_201_CREATED
)
def create_crop(crop_in: CropCreate, db: Session = Depends(get_db)) -> CropResponse:
    crop = Crop(**crop_in.model_dump())
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


@router_crops.put("/{crop_id}", response_model=CropResponse)
def update_crop(
    crop_id: uuid.UUID, crop_in: CropCreate, db: Session = Depends(get_db)
) -> CropResponse:
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
        )
    for key, value in crop_in.model_dump(exclude_unset=True).items():
        setattr(crop, key, value)
    db.commit()
    db.refresh(crop)
    return crop


@router_crops.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_crop(crop_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
        )
    db.delete(crop)
    db.commit()
