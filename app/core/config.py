from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, List, Union
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
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
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000", 
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173"
    ]
    
    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith('['):
            return [i.strip() for i in v.split(',')]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Environment settings
    ENVIRONMENT: str = Field(default="development", description="Environment")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_provider(self) -> str:
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
        return self.database_provider == "sqlite"
    
    @property
    def is_postgresql(self) -> bool:
        return self.database_provider == "postgresql"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()