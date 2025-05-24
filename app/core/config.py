from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """
    Application configuration using Pydantic settings.
    This approach provides automatic validation and environment variable loading.
    """
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Event Management API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Collaborative Event Management System with versioning"
    
    # Security Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database Configuration
    # PostgreSQL provides ACID properties which help with our transaction requirements
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/event_management"
    
    # Redis Configuration (for caching and rate limiting)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
# Create a global settings instance
settings = Settings()