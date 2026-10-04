from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str 
    RABBITMQ_URL: str 
    JWT_SECRET_KEY: str 
    JWT_ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    CORS_ORIGINS: str
    ENVIRONMENT: str 
    GEMINI_API_KEY: str 
    GEMINI_MODEL: str 
    REFUND_WORKER_TIMEOUT_SECONDS: int 
    REFUND_WINDOW_DAYS: int
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.CORS_ORIGINS.split(",") if item.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
