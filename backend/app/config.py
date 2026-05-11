from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Try to load from .env in current dir (backend/) or parent dir (project root)
    model_config = SettingsConfigDict(
        env_file=[
            ".env",
            "../.env",
            str(BASE_DIR / ".env"),
            str(BASE_DIR.parent / ".env")
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Settings
    app_name: str = "MasterDataCleaner API"
    debug: bool = False
    secret_key: str = "your-secret-key-here"

    # Frontend URL (for OAuth redirects)
    # Automatically detects from environment if not set
    # Koyeb provides: KOYEB_PUBLIC_DOMAIN
    # Other platforms may provide: APP_URL, FRONTEND_URL, ORIGIN_URL, URL
    frontend_url: str = ""

    @field_validator("frontend_url", mode="before")
    @classmethod
    def get_frontend_url(cls, v: str) -> str:
        """Get frontend URL from environment or use default."""
        # If value is provided (e.g. from .env), use it
        if v:
            return v
            
        import os
        # Check common deployment platform env vars
        for env_var in ["KOYEB_PUBLIC_DOMAIN", "APP_URL", "FRONTEND_URL", "ORIGIN_URL", "URL"]:
            if env_var in os.environ and os.environ[env_var]:
                return os.environ[env_var]
        # Default for local development
        return "http://localhost:5173"

    # Admin user credentials (optional - if set, creates admin on startup)
    admin_email: str = ""
    admin_password: str = ""

    # CORS - dynamically generated from frontend_url
    @property
    def cors_origins(self) -> list[str]:
        return [self.frontend_url, f"{self.frontend_url}/"]

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

    # Document Knowledge Base
    doc_storage_path: str = "/tmp/masterdatacleaner_docs"
    doc_max_file_size_mb: int = 50
    doc_cleanup_ttl_seconds: int = 3600


@lru_cache
def get_settings() -> Settings:
    return Settings()
