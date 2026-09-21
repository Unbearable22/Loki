from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    log_level: str = "INFO"

    telegram_bot_token: str
    telegram_webhook_secret: str
    telegram_use_webhook: bool = True
    public_webhook_url: str = ""

    backend_base_url: str
    backend_service_token: str = ""
    backend_timeout_seconds: float = 15
    backend_max_retries: int = 3

    database_url: str
    redis_url: str

    cargo_webhook_secret: str = ""
    backend_event_secret: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
