from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings

# Database engine configuration based on provider
def create_database_engine():
    """Create database engine based on the database provider."""
    
    if settings.is_sqlite:
        # SQLite configuration
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={
                "check_same_thread": False,  # Needed for SQLite with FastAPI
                "timeout": 20  # Connection timeout
            },
            poolclass=StaticPool,  # Use static pool for SQLite
            echo=settings.DEBUG  # Log SQL queries in debug mode
        )
        
        # Enable foreign key constraints for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")  # Better concurrency
            cursor.close()
            
    elif settings.is_postgresql:
        # PostgreSQL configuration
        engine = create_engine(
            settings.DATABASE_URL,
            pool_size=10,  # Connection pool size
            max_overflow=20,  # Max connections above pool_size
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,  # Recycle connections every hour
            echo=settings.DEBUG
        )
        
    else:
        # Generic configuration for other databases
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG
        )
    
    return engine

# Create engine
engine = create_database_engine()

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

def init_db():
    """Initialize database tables."""
    # Import all models to ensure they're registered
    from app.models import User, Event, EventPermission, EventVersion
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_db_info():
    """Get database information for health checks."""
    return {
        "provider": settings.database_provider,
        "url_masked": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "local",
        "is_connected": True  # You can add actual connection check here
    }

def test_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False