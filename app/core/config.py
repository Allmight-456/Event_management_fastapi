from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
import os
from pathlib import Path

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    Comprehensive configuration for all integrations.
    """
    
    # Application settings
    PROJECT_NAME: str = "Event Management API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Collaborative Event Management System with versioning"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DATABASE_URL: str = Field(
        default="sqlite:///./event_management.db",
        description="Database connection URL"
    )
    
    # Security settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production-this-should-be-very-long-and-random",
        description="Secret key for JWT tokens"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis configuration
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis URL for rate limiting and caching"
    )
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173"
    ]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Environment settings
    ENVIRONMENT: str = Field(default="development", description="Environment (development/staging/production)")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    
    # Email configuration (for future notifications)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # File storage configuration
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    
    # External API configuration (for calendar integrations)
    GOOGLE_CALENDAR_CLIENT_ID: Optional[str] = None
    GOOGLE_CALENDAR_CLIENT_SECRET: Optional[str] = None
    OUTLOOK_CLIENT_ID: Optional[str] = None
    OUTLOOK_CLIENT_SECRET: Optional[str] = None
    
    # Webhook URLs for notifications
    SLACK_WEBHOOK_URL: Optional[str] = None
    DISCORD_WEBHOOK_URL: Optional[str] = None
    
    # Monitoring and logging
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_provider(self) -> str:
        """Detect database provider from URL."""
        if self.DATABASE_URL.startswith("sqlite"):
            return "sqlite"
        elif self.DATABASE_URL.startswith("postgresql"):
            return "postgresql"
        elif self.DATABASE_URL.startswith("mysql"):
            return "mysql"
        else:
            return "unknown"
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_provider == "sqlite"
    
    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.database_provider == "postgresql"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()