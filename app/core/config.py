from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    Uses SQLite for development by default to avoid PostgreSQL dependency.
    """
    
    # Application settings
    PROJECT_NAME: str = "Event Management API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings - using SQLite for development
    DATABASE_URL: str = Field(
        default="sqlite:///./event_management.db",
        description="Database connection URL"
    )
    
    # For production, you can override with PostgreSQL:
    # DATABASE_URL: str = "postgresql://user:password@localhost/event_management"
    
    # Security settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production-this-should-be-very-long-and-random",
        description="Secret key for JWT tokens"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Rate limiting (if Redis is available)
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis URL for rate limiting (optional)"
    )
    
    # Development settings
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()