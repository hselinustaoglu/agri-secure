from fastapi import FastAPI

from .routers import (
    alerts_router,
    farmers_router,
    food_security_router,
    ingestion_router,
    markets_router,
    regions_router,
    weather_router,
)
from .routers.alerts import router_notifications, router_rules
from .routers.external_data import router as external_data_router
from .routers.farmers import router_crops, router_farms
from .routers.markets import router_price_alerts, router_prices
from .routers.regions import router_zones
from .routers.weather import router_rainfall, router_soil
from .routers.ingestion import router_logs, router_schedules

app = FastAPI(
    title="AgriSecure API",
    description="Unified Food Security & Agriculture Support Platform API",
    version="1.0.0",
)

PREFIX = "/api/v1"

app.include_router(farmers_router, prefix=PREFIX)
app.include_router(router_farms, prefix=PREFIX)
app.include_router(router_crops, prefix=PREFIX)
app.include_router(markets_router, prefix=PREFIX)
app.include_router(router_prices, prefix=PREFIX)
app.include_router(router_price_alerts, prefix=PREFIX)
app.include_router(alerts_router, prefix=PREFIX)
app.include_router(router_rules, prefix=PREFIX)
app.include_router(router_notifications, prefix=PREFIX)
app.include_router(weather_router, prefix=PREFIX)
app.include_router(router_rainfall, prefix=PREFIX)
app.include_router(router_soil, prefix=PREFIX)
app.include_router(regions_router, prefix=PREFIX)
app.include_router(router_zones, prefix=PREFIX)
app.include_router(food_security_router, prefix=PREFIX)
app.include_router(ingestion_router, prefix=PREFIX)
app.include_router(router_logs, prefix=PREFIX)
app.include_router(router_schedules, prefix=PREFIX)
app.include_router(external_data_router, prefix=PREFIX)


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy", "service": "agrisecure-api"}


@app.get("/")
def root() -> dict:
    return {
        "name": "AgriSecure API",
        "description": "Unified Food Security & Agriculture Support Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
