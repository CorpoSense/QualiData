from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App Settings
    app_name: str = "MasterDataCleaner API"
    debug: bool = False
    secret_key: str = "your-secret-key-here"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    database_url: str = "sqlite+aiosqlite:///./master_data_cleaner.db"

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate that database_url is properly formatted."""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        # Check for placeholder values
        if (
            "host:port" in v
            or v == "postgresql://user:password@host:port/database?sslmode=require"
        ):
            raise ValueError(
                "DATABASE_URL contains placeholder values. "
                "Please set a valid DATABASE_URL environment variable."
            )
        return v

    # Connection Pool Settings
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600

    # AI Provider Keys
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    groq_api_key: str | None = None
    deepseek_api_key: str | None = None
    openrouter_api_key: str | None = None

    # OAuth
    google_client_id: str | None = None
    google_client_secret: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None

    # Billing (Lago)
    lago_api_key: str | None = None
    lago_webhook_secret: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
