from .alerts import router as alerts_router
from .farmers import router as farmers_router
from .food_security import router as food_security_router
from .ingestion import router as ingestion_router
from .markets import router as markets_router
from .regions import router as regions_router
from .weather import router as weather_router

__all__ = [
    "farmers_router",
    "markets_router",
    "alerts_router",
    "weather_router",
    "regions_router",
    "food_security_router",
    "ingestion_router",
]
