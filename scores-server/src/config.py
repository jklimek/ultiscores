"""Application configuration using Pydantic settings."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./scores.db"
    
    # API
    api_v1_prefix: str = "/v1"
    project_name: str = "Scores API"
    debug: bool = True
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # WebSocket
    ws_heartbeat_interval: int = 30  # seconds
    
    # JWT (for future authentication)
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()

