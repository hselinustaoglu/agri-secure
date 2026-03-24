import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.market import Market, MarketPrice, PriceAlert
from ..schemas.market import (
    MarketCreate,
    MarketPriceCreate,
    MarketPriceResponse,
    MarketResponse,
    PriceAlertCreate,
    PriceAlertResponse,
)

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("/", response_model=List[MarketResponse])
def list_markets(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[MarketResponse]:
    return db.query(Market).offset(skip).limit(limit).all()


@router.get("/{market_id}", response_model=MarketResponse)
def get_market(market_id: uuid.UUID, db: Session = Depends(get_db)) -> MarketResponse:
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Market not found"
        )
    return market


@router.post("/", response_model=MarketResponse, status_code=status.HTTP_201_CREATED)
def create_market(
    market_in: MarketCreate, db: Session = Depends(get_db)
) -> MarketResponse:
    market = Market(**market_in.model_dump())
    db.add(market)
    db.commit()
    db.refresh(market)
    return market


@router.put("/{market_id}", response_model=MarketResponse)
def update_market(
    market_id: uuid.UUID, market_in: MarketCreate, db: Session = Depends(get_db)
) -> MarketResponse:
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Market not found"
        )
    for key, value in market_in.model_dump(exclude_unset=True).items():
        setattr(market, key, value)
    db.commit()
    db.refresh(market)
    return market


@router.delete("/{market_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_market(market_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Market not found"
        )
    db.delete(market)
    db.commit()


router_prices = APIRouter(prefix="/market-prices", tags=["market-prices"])


@router_prices.get("/", response_model=List[MarketPriceResponse])
def list_prices(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[MarketPriceResponse]:
    return db.query(MarketPrice).offset(skip).limit(limit).all()


@router_prices.get("/{price_id}", response_model=MarketPriceResponse)
def get_price(
    price_id: uuid.UUID, db: Session = Depends(get_db)
) -> MarketPriceResponse:
    price = db.query(MarketPrice).filter(MarketPrice.id == price_id).first()
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Market price not found"
        )
    return price


@router_prices.post(
    "/", response_model=MarketPriceResponse, status_code=status.HTTP_201_CREATED
)
def create_price(
    price_in: MarketPriceCreate, db: Session = Depends(get_db)
) -> MarketPriceResponse:
    price = MarketPrice(**price_in.model_dump())
    db.add(price)
    db.commit()
    db.refresh(price)
    return price


@router_prices.put("/{price_id}", response_model=MarketPriceResponse)
def update_price(
    price_id: uuid.UUID,
    price_in: MarketPriceCreate,
    db: Session = Depends(get_db),
) -> MarketPriceResponse:
    price = db.query(MarketPrice).filter(MarketPrice.id == price_id).first()
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Market price not found"
        )
    for key, value in price_in.model_dump(exclude_unset=True).items():
        setattr(price, key, value)
    db.commit()
    db.refresh(price)
    return price


@router_prices.delete("/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_price(price_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    price = db.query(MarketPrice).filter(MarketPrice.id == price_id).first()
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Market price not found"
        )
    db.delete(price)
    db.commit()


router_price_alerts = APIRouter(prefix="/price-alerts", tags=["price-alerts"])


@router_price_alerts.get("/", response_model=List[PriceAlertResponse])
def list_price_alerts(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[PriceAlertResponse]:
    return db.query(PriceAlert).offset(skip).limit(limit).all()


@router_price_alerts.get("/{alert_id}", response_model=PriceAlertResponse)
def get_price_alert(
    alert_id: uuid.UUID, db: Session = Depends(get_db)
) -> PriceAlertResponse:
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Price alert not found"
        )
    return alert


@router_price_alerts.post(
    "/", response_model=PriceAlertResponse, status_code=status.HTTP_201_CREATED
)
def create_price_alert(
    alert_in: PriceAlertCreate, db: Session = Depends(get_db)
) -> PriceAlertResponse:
    alert = PriceAlert(**alert_in.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router_price_alerts.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_price_alert(alert_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Price alert not found"
        )
    db.delete(alert)
    db.commit()
