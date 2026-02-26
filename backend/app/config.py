from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # App Settings
    app_name: str = "MasterDataCleaner API"
    debug: bool = False
    secret_key: str = "your-secret-key-here"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Database
    database_url: str = "postgresql://user:password@host:port/database?sslmode=require"
    
    # AI Provider Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    
    # Billing (Lago)
    lago_api_key: Optional[str] = None
    lago_webhook_secret: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
