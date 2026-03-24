from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://agrisecure:changeme@localhost:5432/agrisecure"
    REDIS_URL: str = "redis://localhost:6379/0"
    S3_ENDPOINT: str = ""
    S3_BUCKET: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    DEBUG: bool = False
    API_VERSION: str = "v1"
    APP_NAME: str = "AgriSecure API"


settings = Settings()
