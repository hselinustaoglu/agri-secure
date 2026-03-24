from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # === Database (Supabase) ===
    DATABASE_URL: str = (
        "postgresql://postgres.ref:password@aws-0-region.pooler.supabase.com:6543/postgres"
    )
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # === Cache (Upstash Redis) ===
    REDIS_URL: str = "redis://localhost:6379/0"

    # === External API Base URLs ===
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    FAOSTAT_BASE_URL: str = "https://fenixservices.fao.org/faostat/api/v1"
    WFP_API_BASE_URL: str = "https://api.wfp.org/vam-data-bridges/4.0.0"
    WORLD_BANK_RTFP_URL: str = "https://microdata.worldbank.org/index.php/catalog/4483"
    FEWS_NET_BASE_URL: str = "https://fews.net/api"
    HDX_API_BASE_URL: str = "https://data.humdata.org/api/3"

    # === Cache TTL Settings (seconds) ===
    CACHE_TTL_WEATHER: int = 3600
    CACHE_TTL_PRICES: int = 86400
    CACHE_TTL_FOOD_SECURITY: int = 604800

    # === App Settings ===
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    APP_NAME: str = "AgriSecure API"
    LOG_LEVEL: str = "INFO"

    # === ETL Settings ===
    TARGET_COUNTRIES: str = "KEN,ETH,NGA"
    WEATHER_LOCATIONS: str = "-1.286389,36.817223;9.145000,40.489673;9.082000,8.675277"


settings = Settings()
