from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Database engine configuration
# For SQLite, we need to enable foreign key constraints and configure connection args
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite with FastAPI
        echo=settings.DEBUG  # Log SQL queries in debug mode
    )
else:
    # For PostgreSQL or other databases
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """
    Database dependency for FastAPI endpoints.
    Ensures proper connection handling and cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()