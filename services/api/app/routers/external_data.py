"""Router for on-demand external data queries."""

import datetime
import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from ..config import settings
from ..external.cache import RedisCache
from ..external.chirps import CHIRPSClient
from ..external.faostat import FAOSTATClient
from ..external.fews_net import FEWSNetClient
from ..external.heigit import HeiGITClient
from ..external.open_meteo import OpenMeteoClient
from ..external.wfp import WFPClient
from ..external.world_bank import WorldBankClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/external", tags=["external-data"])


def _open_meteo() -> OpenMeteoClient:
    return OpenMeteoClient(
        redis_url=settings.REDIS_URL,
        base_url=settings.OPEN_METEO_BASE_URL,
        ttl=settings.CACHE_TTL_WEATHER,
    )


def _faostat() -> FAOSTATClient:
    return FAOSTATClient(
        redis_url=settings.REDIS_URL,
        base_url=settings.FAOSTAT_BASE_URL,
        ttl=settings.CACHE_TTL_PRICES,
    )


def _world_bank() -> WorldBankClient:
    return WorldBankClient(
        redis_url=settings.REDIS_URL,
        base_url=settings.WORLD_BANK_RTFP_URL,
        ttl=settings.CACHE_TTL_PRICES,
    )


def _wfp() -> WFPClient:
    return WFPClient(
        redis_url=settings.REDIS_URL,
        base_url=settings.WFP_API_BASE_URL,
        ttl=settings.CACHE_TTL_PRICES,
    )


def _fews_net() -> FEWSNetClient:
    return FEWSNetClient(
        redis_url=settings.REDIS_URL,
        base_url=settings.FEWS_NET_BASE_URL,
        ttl=settings.CACHE_TTL_FOOD_SECURITY,
    )


def _chirps() -> CHIRPSClient:
    return CHIRPSClient(
        redis_url=settings.REDIS_URL,
        ttl=settings.CACHE_TTL_PRICES,
    )


def _heigit() -> HeiGITClient:
    return HeiGITClient(
        redis_url=settings.REDIS_URL,
        base_url=settings.HDX_API_BASE_URL,
        ttl=settings.CACHE_TTL_FOOD_SECURITY,
    )


@router.get("/weather")
async def get_weather(
    lat: float = Query(..., description="Latitude (WGS-84)"),
    lon: float = Query(..., description="Longitude (WGS-84)"),
    daily: Optional[str] = Query(
        None,
        description="Comma-separated daily variables (Open-Meteo). "
        "Defaults to temperature_2m_max,precipitation_sum,soil_moisture_0_to_7cm",
    ),
) -> Any:
    """Proxy weather forecast from Open-Meteo (cached 1 hour)."""
    try:
        return await _open_meteo().get_forecast(lat, lon, daily)
    except Exception as exc:
        logger.error("Open-Meteo request failed: %s", exc)
        raise HTTPException(
            status_code=502, detail=f"Open-Meteo unavailable: {exc}"
        ) from exc


@router.get("/prices")
async def get_prices(
    country: str = Query(..., description="ISO3 country code, e.g. KEN"),
    crop: Optional[str] = Query(None, description="Crop/commodity name"),
) -> Any:
    """Query food prices from World Bank RTFP and WFP (cached 24 hours)."""
    wb_client = _world_bank()
    wfp_client = _wfp()
    results: dict = {}

    try:
        results["world_bank"] = await wb_client.get_catalog()
    except Exception as exc:
        logger.warning("World Bank prices unavailable: %s", exc)
        results["world_bank"] = None

    try:
        results["wfp"] = await wfp_client.get_prices(
            country_code=country, commodity=crop
        )
    except Exception as exc:
        logger.warning("WFP prices unavailable: %s", exc)
        results["wfp"] = None

    if results["world_bank"] is None and results["wfp"] is None:
        raise HTTPException(
            status_code=502, detail="All price data sources unavailable"
        )

    return results


@router.get("/food-security")
async def get_food_security(
    country: str = Query(..., description="ISO3 country code, e.g. KEN"),
) -> Any:
    """Query food security data from FEWS NET and FAOSTAT (cached 7 days)."""
    fews_client = _fews_net()
    fao_client = _faostat()
    results: dict = {}

    try:
        results["fews_net"] = await fews_client.get_ipc_data(country_code=country)
    except Exception as exc:
        logger.warning("FEWS NET unavailable: %s", exc)
        results["fews_net"] = None

    try:
        results["faostat"] = await fao_client.get_data(domain="FS", area=country)
    except Exception as exc:
        logger.warning("FAOSTAT unavailable: %s", exc)
        results["faostat"] = None

    if results["fews_net"] is None and results["faostat"] is None:
        raise HTTPException(
            status_code=502, detail="All food security sources unavailable"
        )

    return results


@router.get("/rainfall")
async def get_rainfall(
    country: str = Query(..., description="ISO3 country code, e.g. KEN"),
    year: Optional[int] = Query(None, description="4-digit year"),
    month: Optional[int] = Query(None, description="Month number 1-12"),
) -> Any:
    """Return CHIRPS monthly rainfall file metadata (cached 24 hours)."""
    if year is None or month is None:
        now = datetime.datetime.utcnow()
        if month is None:
            month = now.month - 1 if now.month > 1 else 12
            if year is None:
                year = now.year if now.month > 1 else now.year - 1
        elif year is None:
            year = now.year

    try:
        return await _chirps().get_monthly_stats(
            year=year, month=month, country=country
        )
    except Exception as exc:
        logger.error("CHIRPS request failed: %s", exc)
        raise HTTPException(
            status_code=502, detail=f"CHIRPS unavailable: {exc}"
        ) from exc


@router.get("/risk")
async def get_risk(
    country: Optional[str] = Query(None, description="ISO3 country code, e.g. MW"),
) -> Any:
    """Query HeiGIT risk and accessibility datasets from HDX (cached 7 days)."""
    heigit_client = _heigit()
    results: dict = {}

    try:
        results["risk"] = await heigit_client.get_risk_datasets(country=country)
    except Exception as exc:
        logger.warning("HeiGIT risk unavailable: %s", exc)
        results["risk"] = None

    try:
        results["accessibility"] = await heigit_client.get_accessibility_datasets(
            country=country
        )
    except Exception as exc:
        logger.warning("HeiGIT accessibility unavailable: %s", exc)
        results["accessibility"] = None

    if results["risk"] is None and results["accessibility"] is None:
        raise HTTPException(status_code=502, detail="HeiGIT data unavailable")

    return results


@router.get("/cache/status")
async def cache_status() -> Any:
    """Return Redis cache statistics (hit/miss metrics and memory usage)."""
    cache = RedisCache(settings.REDIS_URL)
    return {"status": "ok", "redis": cache.stats()}
